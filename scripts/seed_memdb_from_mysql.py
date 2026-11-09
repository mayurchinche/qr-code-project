"""One-time migration: copy product_details + product_queries into the first
in-memory-database snapshot, from either a live MySQL or a mysqldump file.

    # from live MySQL (.env: DB_HOST, DB_PORT, DB_USER, DB_PASSWORD, DB_NAME)
    python scripts/seed_memdb_from_mysql.py --out seed.sqlite
    # from a mysqldump .sql file (e.g. the Drive backup)
    python scripts/seed_memdb_from_mysql.py --from-dump db_backup.sql --out seed.sqlite

    # add --upload to store it as the live snapshot (GDRIVE_FOLDER_ID + credentials from env)

Refuses to overwrite an existing snapshot in the store unless --force is given.
"""
import argparse
import os
import re
import sqlite3
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from dotenv import load_dotenv  # noqa: E402

load_dotenv()

from memdb import SCHEMA, _conn_to_bytes  # noqa: E402

TABLES = {
    "product_details": ["model_name", "serial_number", "mfg_year", "material_url", "created_at"],
    "product_queries": ["id", "model_name", "serial_number", "mfg_year", "customer_gmail",
                        "customer_city", "company_name", "created_at"],
}


def fetch_mysql():
    import mysql.connector

    conn = mysql.connector.connect(
        host=os.getenv("DB_HOST"), port=int(os.getenv("DB_PORT", "3306")),
        user=os.getenv("DB_USER"), password=os.getenv("DB_PASSWORD"), database=os.getenv("DB_NAME"),
    )
    try:
        cur = conn.cursor()
        cur.execute("SET time_zone = '+00:00'")  # created_at stays UTC, same as SQLite CURRENT_TIMESTAMP
        data = {}
        for table, cols in TABLES.items():
            cur.execute(f"SELECT {', '.join(cols)} FROM {table}")
            data[table] = cur.fetchall()
        return data
    finally:
        conn.close()


_MYSQL_ESCAPES = {"0": "\0", "b": "\b", "n": "\n", "r": "\r", "t": "\t", "Z": "\x1a"}


def _parse_values(text: str):
    """Parse mysqldump extended-insert tuples: (v,v,...),(v,...) -> list of tuples."""
    rows, row, i, n = [], None, 0, len(text)
    while i < n:
        c = text[i]
        if c == "(":
            row = []
            i += 1
        elif c == ")":
            rows.append(tuple(row))
            row = None
            i += 1
        elif c in ", ;\n\r\t":
            i += 1
        elif c == "'":
            i += 1
            buf = []
            while True:
                ch = text[i]
                if ch == "\\":
                    nxt = text[i + 1]
                    buf.append(_MYSQL_ESCAPES.get(nxt, nxt))
                    i += 2
                elif ch == "'":
                    if i + 1 < n and text[i + 1] == "'":  # '' inside a string
                        buf.append("'")
                        i += 2
                    else:
                        i += 1
                        break
                else:
                    buf.append(ch)
                    i += 1
            row.append("".join(buf))
        else:
            m = re.match(r"NULL|-?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?", text[i:])
            if not m or row is None:
                raise ValueError(f"Unexpected token near: {text[i:i + 40]!r}")
            tok = m.group(0)
            row.append(None if tok == "NULL" else (float(tok) if any(x in tok for x in ".eE") else int(tok)))
            i += len(tok)
    return rows


def fetch_dump(path: str):
    """Read the two tables from a mysqldump file (column order must match TABLES)."""
    with open(path, encoding="utf-8") as f:
        sql = f.read()
    data = {}
    for table, cols in TABLES.items():
        create = re.search(rf"CREATE TABLE `{table}` \((.*?)\n\) ENGINE", sql, re.S)
        if not create:
            raise SystemExit(f"Table {table} not found in {path}")
        dump_cols = re.findall(r"^\s+`(\w+)`", create.group(1), re.M)
        if dump_cols != cols:
            raise SystemExit(f"Unexpected columns for {table}: {dump_cols}")
        rows = []
        for m in re.finditer(rf"^INSERT INTO `{table}` VALUES (.*);$", sql, re.M):
            rows.extend(_parse_values(m.group(1)))
        bad = [r for r in rows if len(r) != len(cols)]
        if bad:
            raise SystemExit(f"{len(bad)} malformed row(s) parsed for {table}")
        data[table] = rows
    return data


def build_snapshot(data) -> bytes:
    mem = sqlite3.connect(":memory:")
    mem.executescript(SCHEMA)
    for table, cols in TABLES.items():
        rows = []
        for row in data[table]:
            rows.append(tuple(
                v.strftime("%Y-%m-%d %H:%M:%S") if hasattr(v, "strftime") else v for v in row
            ))
        mem.executemany(
            f"INSERT INTO {table} ({', '.join(cols)}) VALUES ({', '.join('?' for _ in cols)})", rows
        )
    mem.commit()
    for table in TABLES:
        n = mem.execute(f"SELECT COUNT(*) FROM {table}").fetchone()[0]
        if n != len(data[table]):
            raise SystemExit(f"Row count mismatch for {table}: mysql={len(data[table])} sqlite={n}")
        print(f"  {table}: {n} rows")
    return _conn_to_bytes(mem)


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--from-dump", metavar="SQL_FILE", help="read rows from a mysqldump file instead of MySQL")
    parser.add_argument("--out", help="write the snapshot to this local file")
    parser.add_argument("--upload", action="store_true", help="upload as the live snapshot (MEMDB_STORE)")
    parser.add_argument("--force", action="store_true", help="overwrite an existing snapshot in the store")
    args = parser.parse_args()
    if not args.out and not args.upload:
        parser.error("use --out FILE and/or --upload")

    if args.from_dump:
        print(f"Reading dump {args.from_dump} ...")
        data = fetch_dump(args.from_dump)
    else:
        print(f"Reading MySQL {os.getenv('DB_HOST')}/{os.getenv('DB_NAME')} ...")
        data = fetch_mysql()
    snapshot = build_snapshot(data)

    if args.out:
        with open(args.out, "wb") as f:
            f.write(snapshot)
        print(f"Wrote {args.out} ({len(snapshot)} bytes)")

    if args.upload:
        if os.getenv("MEMDB_STORE", "drive").lower() == "local":
            from snapshot_store import LocalFileStore
            store = LocalFileStore(os.getenv("MEMDB_LOCAL_DIR", "memdb_data"))
        else:
            from snapshot_store import DriveStore
            store = DriveStore.from_env()
        existing = store.remote_version()
        if existing is not None and not args.force:
            raise SystemExit(f"A snapshot (version {existing}) already exists; use --force to overwrite it")
        version = (existing or 0) + 1
        store.save(snapshot, version)
        print(f"Uploaded snapshot version {version}")


if __name__ == "__main__":
    main()
