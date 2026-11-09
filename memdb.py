"""In-memory SQLite database that is durably backed by a SnapshotStore (Google Drive).

Lifecycle
- start():  restore the latest snapshot into memory, then start the backup thread.
            Refuses to start empty (unless MEMDB_ALLOW_EMPTY=true) so a failed or
            missing restore can never overwrite good backups with an empty database.
- write():  every committed write bumps a sequence number and wakes the backup
            thread. Requests return immediately; uploads happen in the background.
            Bursts of writes are coalesced into one upload.
- stop():   final upload on shutdown (SIGTERM from Render), bounded by a timeout.

Safety
- Failed uploads are retried with exponential backoff until they succeed.
- Each snapshot carries a version. If the stored version changed underneath us
  (e.g. two instances overlapping during a deploy), the remote rows are merged
  into memory before uploading, instead of overwriting them.
- A dated copy is kept per day (MEMDB_KEEP_DAYS, default 30) for rollback.

Run exactly ONE process (one Render instance, one gunicorn/uvicorn worker):
every process has its own in-memory copy.
"""
import logging
import os
import sqlite3
import tempfile
import threading
import time
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Dict, List, Optional

from snapshot_store import SnapshotStore

log = logging.getLogger("memdb")

SCHEMA = """
CREATE TABLE IF NOT EXISTS product_details (
    model_name    TEXT NOT NULL COLLATE NOCASE,
    serial_number TEXT NOT NULL COLLATE NOCASE,
    mfg_year      TEXT NOT NULL COLLATE NOCASE,
    material_url  TEXT NOT NULL,
    created_at    TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (model_name, serial_number)
);
CREATE TABLE IF NOT EXISTS product_queries (
    id             INTEGER PRIMARY KEY AUTOINCREMENT,
    model_name     TEXT NOT NULL COLLATE NOCASE,
    serial_number  TEXT NOT NULL COLLATE NOCASE,
    mfg_year       TEXT NOT NULL COLLATE NOCASE,
    customer_gmail TEXT NOT NULL COLLATE NOCASE,
    customer_city  TEXT NOT NULL,
    company_name   TEXT NOT NULL,
    created_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
"""

# Columns ignored when deciding whether a remote row already exists locally (merge).
MERGE_IGNORE_COLUMNS: Dict[str, List[str]] = {
    "product_details": [],
    "product_queries": ["id"],
}


def _convert_timestamp(value: bytes):
    try:
        return datetime.fromisoformat(value.decode())
    except ValueError:
        return None


# Return TIMESTAMP columns as datetime (MySQL connector behaviour the app relies on).
sqlite3.register_converter("TIMESTAMP", _convert_timestamp)


def _env_bool(name: str, default: bool = False) -> bool:
    return os.getenv(name, str(default)).strip().lower() in ("1", "true", "yes")


def _bytes_to_conn(data: bytes, target: sqlite3.Connection) -> None:
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    try:
        with os.fdopen(fd, "wb") as f:
            f.write(data)
        src = sqlite3.connect(path)
        try:
            result = src.execute("PRAGMA integrity_check").fetchone()[0]
            if result != "ok":
                raise RuntimeError(f"Snapshot failed integrity check: {result}")
            src.backup(target)
        finally:
            src.close()
    finally:
        os.unlink(path)


def _conn_to_bytes(source: sqlite3.Connection) -> bytes:
    fd, path = tempfile.mkstemp(suffix=".sqlite")
    os.close(fd)
    try:
        dst = sqlite3.connect(path)
        try:
            source.backup(dst)
        finally:
            dst.close()
        with open(path, "rb") as f:
            return f.read()
    finally:
        os.unlink(path)


class MemDB:
    def __init__(
        self,
        store: SnapshotStore,
        allow_empty: bool = False,
        keep_days: int = 30,
        periodic_seconds: float = 300.0,
        max_backoff_seconds: float = 60.0,
    ):
        self.store = store
        self.allow_empty = allow_empty
        self.keep_days = keep_days
        self.periodic_seconds = periodic_seconds
        self.max_backoff_seconds = max_backoff_seconds

        self._conn = sqlite3.connect(":memory:", check_same_thread=False, detect_types=sqlite3.PARSE_DECLTYPES)
        self._lock = threading.RLock()
        self._wake = threading.Event()
        self._stopping = threading.Event()
        self._saved_cond = threading.Condition()
        self._thread: Optional[threading.Thread] = None

        self.version = 0            # version of the snapshot our memory is based on / last uploaded
        self._dirty_seq = 0         # incremented on every committed write
        self._saved_seq = 0         # last write sequence that is safely stored
        self._daily_day: Optional[str] = None
        self.started = False
        self.last_backup_at: Optional[str] = None
        self.last_error: Optional[str] = None
        self.consecutive_failures = 0
        self.merges = 0

    # ------------------------------------------------------------------ lifecycle
    def start(self) -> None:
        workers = os.getenv("WEB_CONCURRENCY")
        if workers and workers.isdigit() and int(workers) > 1:
            raise RuntimeError(
                f"WEB_CONCURRENCY={workers}: the in-memory database requires exactly one worker process"
            )
        snapshot = self.store.load_latest()  # raises on network/auth errors -> app fails to start (safe)
        with self._lock:
            if snapshot is None:
                if not self.allow_empty:
                    raise RuntimeError(
                        "No database snapshot found in the store. Seed it first "
                        "(scripts/seed_memdb_from_mysql.py) or set MEMDB_ALLOW_EMPTY=true for a brand-new database."
                    )
                log.warning("No snapshot found; starting with an EMPTY database (MEMDB_ALLOW_EMPTY=true)")
                self.version = 0
            else:
                data, self.version = snapshot
                _bytes_to_conn(data, self._conn)
                log.info("Restored snapshot version %s (%d bytes)", self.version, len(data))
            self._conn.executescript(SCHEMA)
            self._conn.commit()
        self._thread = threading.Thread(target=self._run, name="memdb-backup", daemon=True)
        self._thread.start()
        self.started = True

    def stop(self, timeout: float = 20.0) -> bool:
        """Flush pending writes and stop the backup thread. Returns True if everything was saved."""
        if not self._thread:
            return True
        self._stopping.set()
        self._wake.set()
        self._thread.join(timeout)
        ok = self._saved_seq >= self._dirty_seq
        if not ok:
            log.error("Shutdown with %d unsaved write(s): %s", self._dirty_seq - self._saved_seq, self.last_error)
        return ok

    # ------------------------------------------------------------------ data access
    def query(self, sql: str, params=()) -> list:
        with self._lock:
            return self._conn.execute(sql, params).fetchall()

    @contextmanager
    def write(self):
        """Transaction; commits and schedules a background backup on success."""
        with self._lock:
            cur = self._conn.cursor()
            try:
                yield cur
                self._conn.commit()
            except BaseException:
                self._conn.rollback()
                raise
            finally:
                cur.close()
            self._dirty_seq += 1
        self._wake.set()

    def flush(self, timeout: float = 30.0) -> bool:
        """Block until all writes made before this call are stored (used by tests/admin)."""
        target = self._dirty_seq
        self._wake.set()
        deadline = time.monotonic() + timeout
        with self._saved_cond:
            while self._saved_seq < target:
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return False
                self._saved_cond.wait(remaining)
        return True

    def status(self) -> dict:
        with self._lock:
            counts = {
                t: self._conn.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
                for t in MERGE_IGNORE_COLUMNS
            }
        return {
            "started": self.started,
            "snapshot_version": self.version,
            "unsaved_writes": self._dirty_seq - self._saved_seq,
            "last_backup_at": self.last_backup_at,
            "last_error": self.last_error,
            "consecutive_failures": self.consecutive_failures,
            "merges": self.merges,
            "row_counts": counts,
        }

    # ------------------------------------------------------------------ backup thread
    def _run(self) -> None:
        backoff = 0.0
        while True:
            wait = backoff or self.periodic_seconds
            if self._stopping.is_set():
                wait = min(wait, 1.0)  # retry quickly within the shutdown window
            self._wake.wait(timeout=wait)
            self._wake.clear()
            if self._saved_seq < self._dirty_seq:
                try:
                    self._backup_once()
                    backoff = 0.0
                except Exception as exc:  # keep retrying; never drop writes
                    self.consecutive_failures += 1
                    self.last_error = f"{type(exc).__name__}: {exc}"
                    backoff = min(self.max_backoff_seconds, 2 ** min(self.consecutive_failures, 6))
                    log.exception("Backup failed (attempt %d), retrying in %.0fs",
                                  self.consecutive_failures, backoff)
            if self._stopping.is_set() and self._saved_seq >= self._dirty_seq:
                return

    def _backup_once(self) -> None:
        remote = self.store.remote_version()
        if remote is not None and remote != self.version:
            self._merge_remote(remote)

        with self._lock:
            seq = self._dirty_seq
            data = _conn_to_bytes(self._conn)
        new_version = self.version + 1
        self.store.save(data, new_version)
        self.version = new_version

        day = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        if self._daily_day != day:
            try:
                self.store.save_daily(data, day, self.keep_days)
                self._daily_day = day
            except Exception:
                log.exception("Daily snapshot copy failed (latest snapshot is saved)")

        self.last_backup_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
        self.last_error = None
        self.consecutive_failures = 0
        with self._saved_cond:
            self._saved_seq = max(self._saved_seq, seq)
            self._saved_cond.notify_all()
        log.info("Backed up snapshot version %s (%d bytes)", new_version, len(data))

    def _merge_remote(self, remote_version: int) -> None:
        """Another writer saved a snapshot we have not seen: merge its rows instead of overwriting."""
        snapshot = self.store.load_latest()
        if snapshot is None:
            return
        data, remote_version = snapshot
        other = sqlite3.connect(":memory:")
        try:
            _bytes_to_conn(data, other)
            added = 0
            with self._lock:
                for table, ignore in MERGE_IGNORE_COLUMNS.items():
                    exists = other.execute(
                        "SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,)
                    ).fetchone()
                    if not exists:
                        continue
                    cols = [r[1] for r in other.execute(f"PRAGMA table_info({table})")]
                    keep = [c for c in cols if c not in ignore]
                    col_list = ", ".join(keep)
                    match = " AND ".join(f"{c} IS ?" for c in keep)
                    placeholders = ", ".join("?" for _ in keep)
                    for row in other.execute(f"SELECT {col_list} FROM {table}"):
                        if self._conn.execute(f"SELECT 1 FROM {table} WHERE {match} LIMIT 1", row).fetchone():
                            continue
                        cur = self._conn.execute(
                            f"INSERT OR IGNORE INTO {table} ({col_list}) VALUES ({placeholders})", row
                        )
                        added += cur.rowcount
                self._conn.commit()
                if added:
                    self._dirty_seq += 1
            self.version = remote_version
            self.merges += 1
            log.warning("Stored snapshot changed (version %s); merged %d remote row(s) into memory",
                        remote_version, added)
        finally:
            other.close()


def create_db_from_env() -> MemDB:
    """Build the app's database from environment variables.

    MEMDB_STORE=drive (default) | local, MEMDB_LOCAL_DIR=./memdb_data (local only),
    GDRIVE_FOLDER_ID, GDRIVE_CREDENTIALS (JSON) or GDRIVE_CREDENTIALS_FILE,
    MEMDB_ALLOW_EMPTY, MEMDB_KEEP_DAYS.
    """
    kind = os.getenv("MEMDB_STORE", "drive").lower()
    if kind == "local":
        from snapshot_store import LocalFileStore
        store = LocalFileStore(os.getenv("MEMDB_LOCAL_DIR", "memdb_data"))
    else:
        from snapshot_store import DriveStore
        store = DriveStore.from_env()
    return MemDB(
        store,
        allow_empty=_env_bool("MEMDB_ALLOW_EMPTY"),
        keep_days=int(os.getenv("MEMDB_KEEP_DAYS", "30")),
    )
