import os
import sqlite3
import sys
import tempfile
import threading
import time
import unittest
from datetime import datetime
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from memdb import MemDB, _bytes_to_conn  # noqa: E402
from snapshot_store import LocalFileStore  # noqa: E402


class CountingStore(LocalFileStore):
    """LocalFileStore that counts saves and can be told to fail or be slow."""

    def __init__(self, directory):
        super().__init__(directory)
        self.saves = 0
        self.fail_next = 0
        self.save_delay = 0.0
        self._mu = threading.Lock()

    def save(self, data, version):
        with self._mu:
            if self.fail_next:
                self.fail_next -= 1
                raise ConnectionError("simulated Drive outage")
        time.sleep(self.save_delay)
        super().save(data, version)
        with self._mu:
            self.saves += 1


def rows_in_store(store, table):
    data, _ = store.load_latest()
    conn = sqlite3.connect(":memory:")
    _bytes_to_conn(data, conn)
    return conn.execute(f"SELECT * FROM {table}").fetchall()


def add_product(db, model, serial="S1", year="2026"):
    with db.write() as cur:
        cur.execute(
            "INSERT INTO product_details (model_name, serial_number, mfg_year, material_url) VALUES (?,?,?,?)",
            (model, serial, year, f"https://x/form?model={model}"),
        )


def add_query(db, email, model="M1"):
    with db.write() as cur:
        cur.execute(
            "INSERT INTO product_queries (model_name, serial_number, mfg_year, customer_gmail, customer_city,"
            " company_name) VALUES (?,?,?,?,?,?)",
            (model, "S1", "2026", email, "Pune", "ACME"),
        )


class MemDBTests(unittest.TestCase):
    def setUp(self):
        self.dir = tempfile.mkdtemp()
        self.store = CountingStore(self.dir)
        self.dbs = []

    def tearDown(self):
        for db in self.dbs:
            db.stop(timeout=5)

    def make(self, **kw):
        kw.setdefault("periodic_seconds", 0.2)
        kw.setdefault("max_backoff_seconds", 0.2)
        db = MemDB(self.store, **kw)
        self.dbs.append(db)
        return db

    def test_refuses_to_start_empty_by_default(self):
        db = self.make()
        with self.assertRaises(RuntimeError):
            db.start()
        self.assertIsNone(self.store.remote_version(), "nothing must be uploaded")

    def test_write_is_backed_up_and_restored_on_restart(self):
        db = self.make(allow_empty=True)
        db.start()
        add_product(db, "M1")
        add_query(db, "a@x.com")
        self.assertTrue(db.flush(5))
        db.stop()

        restarted = self.make()  # no allow_empty: must restore from the store
        restarted.start()
        self.assertEqual(len(restarted.query("SELECT * FROM product_details")), 1)
        (created,) = restarted.query("SELECT created_at FROM product_queries")[0]
        self.assertIsInstance(created, datetime)

    def test_write_returns_before_upload(self):
        db = self.make(allow_empty=True)
        db.start()
        self.store.save_delay = 1.0
        t0 = time.monotonic()
        add_product(db, "M1")
        self.assertLess(time.monotonic() - t0, 0.2, "write must not wait for Drive")
        self.assertTrue(db.flush(5))

    def test_burst_of_writes_is_coalesced(self):
        db = self.make(allow_empty=True)
        db.start()
        self.store.save_delay = 0.3
        for i in range(50):
            add_product(db, f"M{i}")
        self.assertTrue(db.flush(10))
        self.assertLess(self.store.saves, 10)
        self.assertEqual(len(rows_in_store(self.store, "product_details")), 50)

    def test_failed_uploads_are_retried_until_saved(self):
        db = self.make(allow_empty=True)
        db.start()
        self.store.fail_next = 3
        add_product(db, "M1")
        self.assertTrue(db.flush(10))
        status = db.status()
        self.assertEqual(status["unsaved_writes"], 0)
        self.assertIsNone(status["last_error"])
        self.assertEqual(len(rows_in_store(self.store, "product_details")), 1)

    def test_stop_flushes_pending_writes(self):
        db = self.make(allow_empty=True, periodic_seconds=3600)
        db.start()
        self.store.save_delay = 0.3
        add_query(db, "a@x.com")
        add_query(db, "b@x.com")
        self.assertTrue(db.stop(timeout=5))
        self.assertEqual(len(rows_in_store(self.store, "product_queries")), 2)

    def test_overlapping_instances_merge_instead_of_overwrite(self):
        seed = self.make(allow_empty=True)
        seed.start()
        add_product(seed, "M0")
        add_query(seed, "seed@x.com")
        seed.stop()

        old, new = self.make(), self.make()  # deploy overlap: both restore the same version
        old.start()
        new.start()
        add_product(old, "OLD")
        add_query(old, "old@x.com")
        self.assertTrue(old.flush(5))
        add_product(new, "NEW")
        add_query(new, "new@x.com")
        self.assertTrue(new.flush(5))

        models = sorted(r[0] for r in rows_in_store(self.store, "product_details"))
        emails = sorted(r[4] for r in rows_in_store(self.store, "product_queries"))
        self.assertEqual(models, ["M0", "NEW", "OLD"])
        self.assertEqual(emails, ["new@x.com", "old@x.com", "seed@x.com"])
        self.assertEqual(new.merges, 1)

    def test_case_insensitive_like_mysql(self):
        db = self.make(allow_empty=True)
        db.start()
        add_query(db, "User@Gmail.com")
        (n,) = db.query("SELECT COUNT(*) FROM product_queries WHERE customer_gmail = ?", ("user@gmail.com",))[0]
        self.assertEqual(n, 1)

    def test_refuses_multiple_workers(self):
        db = self.make(allow_empty=True)
        with mock.patch.dict(os.environ, {"WEB_CONCURRENCY": "4"}):
            with self.assertRaises(RuntimeError):
                db.start()

    def test_daily_copies_are_pruned(self):
        store = LocalFileStore(self.dir)
        for day in ["2026-01-01", "2026-01-02", "2026-01-03", "2026-01-04"]:
            store.save_daily(b"x", day, keep_days=2)
        dailies = sorted(n for n in os.listdir(self.dir) if n.startswith("qr_app_db_2"))
        self.assertEqual(dailies, ["qr_app_db_2026-01-03.sqlite", "qr_app_db_2026-01-04.sqlite"])


class AppEndpointTests(unittest.TestCase):
    """Exercise the real FastAPI handlers against a local store (no MySQL, no Drive, no email)."""

    def test_endpoints(self):
        d = tempfile.mkdtemp()
        env = {"MEMDB_STORE": "local", "MEMDB_LOCAL_DIR": d, "MEMDB_ALLOW_EMPTY": "true",
               "FRONT_END_API": "https://qr.example.com"}
        with mock.patch.dict(os.environ, env):
            sys.modules.pop("main", None)
            import main
        main.db.start()
        try:
            r = main.generate_qr_url("GALILEO", "SN-1", "2026")
            self.assertEqual(r["url"], "https://qr.example.com/form?model=GALILEO&serial=SN-1&mfg_year=2026")
            self.assertEqual(main.generate_qr_url("GALILEO", "SN-1", "2026")["message"], "Already exists")
            products = main.get_products()
            self.assertEqual(len(products), 1)
            datetime.strptime(products[0]["created_at"], "%Y-%m-%d %H:%M:%S")

            self.assertFalse(main.check_registration("GALILEO", "SN-1", "2026", "c@x.com")["exists"])
            with mock.patch.object(main, "send_email"):
                main.submit_form("c@x.com", "ACME", "Pune", "GALILEO", "SN-1", "2026")
            self.assertTrue(main.check_registration("GALILEO", "SN-1", "2026", "c@x.com")["exists"])
            self.assertEqual(main.get_customer_queries()[0]["customer_gmail"], "c@x.com")
            self.assertTrue(main.db.flush(5))
            self.assertEqual(main.health_db()["unsaved_writes"], 0)
        finally:
            main.db.stop(5)


if __name__ == "__main__":
    unittest.main()
