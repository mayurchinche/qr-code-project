"""Durable storage for in-memory database snapshots.

A store keeps one "latest" snapshot (raw SQLite file bytes) tagged with an
integer version, plus one dated copy per day for point-in-time rollback.

- DriveStore:     Google Drive folder (production)
- LocalFileStore: local directory (development and tests)
"""
import io
import json
import logging
import os
from typing import List, Optional, Tuple

log = logging.getLogger("snapshot_store")

SNAPSHOT_MIME = "application/x-sqlite3"

# Same Drive folder and service account as the GitHub MySQL backup (scripts/upload_to_drive.py).
# Snapshots use their own names/mime type, so neither job's cleanup touches the other's files.
DEFAULT_GDRIVE_FOLDER_ID = "1YzL4tmgyfLOYbzLntlp8yoXBjG2nmbZH"


class SnapshotStore:
    """Interface used by MemDB. All methods may raise on transient failures."""

    def load_latest(self) -> Optional[Tuple[bytes, int]]:
        """Return (snapshot_bytes, version) or None if no snapshot exists yet."""
        raise NotImplementedError

    def remote_version(self) -> Optional[int]:
        """Version of the latest stored snapshot, or None if none exists."""
        raise NotImplementedError

    def save(self, data: bytes, version: int) -> None:
        """Replace the latest snapshot with `data` tagged as `version`."""
        raise NotImplementedError

    def save_daily(self, data: bytes, day: str, keep_days: int) -> None:
        """Store/overwrite the copy for `day` (YYYY-MM-DD) and prune older copies."""
        raise NotImplementedError


class LocalFileStore(SnapshotStore):
    def __init__(self, directory: str, prefix: str = "qr_app_db"):
        self.directory = directory
        self.prefix = prefix
        os.makedirs(directory, exist_ok=True)

    @property
    def _latest(self) -> str:
        return os.path.join(self.directory, f"{self.prefix}_latest.sqlite")

    @property
    def _meta(self) -> str:
        return self._latest + ".json"

    def load_latest(self):
        if not os.path.exists(self._latest):
            return None
        with open(self._latest, "rb") as f:
            data = f.read()
        return data, self.remote_version() or 0

    def remote_version(self):
        if not os.path.exists(self._meta):
            return None
        with open(self._meta) as f:
            return int(json.load(f)["version"])

    def save(self, data, version):
        tmp = self._latest + ".tmp"
        with open(tmp, "wb") as f:
            f.write(data)
        os.replace(tmp, self._latest)
        with open(self._meta + ".tmp", "w") as f:
            json.dump({"version": version}, f)
        os.replace(self._meta + ".tmp", self._meta)

    def save_daily(self, data, day, keep_days):
        with open(os.path.join(self.directory, f"{self.prefix}_{day}.sqlite"), "wb") as f:
            f.write(data)
        dailies = sorted(
            n for n in os.listdir(self.directory)
            if n.startswith(self.prefix + "_2") and n.endswith(".sqlite")
        )
        for name in dailies[:-keep_days] if keep_days > 0 else []:
            os.remove(os.path.join(self.directory, name))


class DriveStore(SnapshotStore):
    """Google Drive folder store using a service account.

    Not thread-safe (httplib2); MemDB only calls it from one thread at a time.
    """

    def __init__(self, service, folder_id: str, prefix: str = "qr_app_db"):
        self.service = service
        self.folder_id = folder_id
        self.prefix = prefix
        self._latest_id: Optional[str] = None

    @classmethod
    def from_env(cls) -> "DriveStore":
        from google.oauth2 import service_account
        from googleapiclient.discovery import build

        folder_id = os.getenv("GDRIVE_FOLDER_ID", DEFAULT_GDRIVE_FOLDER_ID)
        scopes = ["https://www.googleapis.com/auth/drive"]
        raw = os.getenv("GDRIVE_CREDENTIALS")
        if raw:
            creds = service_account.Credentials.from_service_account_info(json.loads(raw), scopes=scopes)
        else:
            path = os.getenv("GDRIVE_CREDENTIALS_FILE", "credentials.json")
            creds = service_account.Credentials.from_service_account_file(path, scopes=scopes)
        service = build("drive", "v3", credentials=creds, cache_discovery=False)
        return cls(service, folder_id, prefix=os.getenv("MEMDB_SNAPSHOT_PREFIX", "qr_app_db"))

    # -- helpers -----------------------------------------------------------
    def _find(self, name: str) -> List[dict]:
        q = f"'{self.folder_id}' in parents and name = '{name}' and trashed = false"
        resp = self.service.files().list(
            q=q, fields="files(id, name, appProperties, modifiedTime)", orderBy="modifiedTime desc",
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        return resp.get("files", [])

    @property
    def _latest_name(self) -> str:
        return f"{self.prefix}_latest.sqlite"

    def _latest_file(self) -> Optional[dict]:
        files = self._find(self._latest_name)
        if len(files) > 1:
            log.warning("Multiple '%s' files in Drive folder; using most recently modified", self._latest_name)
        self._latest_id = files[0]["id"] if files else None
        return files[0] if files else None

    def _upload(self, name: str, data: bytes, file_id: Optional[str], app_properties: Optional[dict] = None) -> str:
        from googleapiclient.http import MediaIoBaseUpload

        media = MediaIoBaseUpload(io.BytesIO(data), mimetype=SNAPSHOT_MIME, resumable=False)
        body = {"name": name}
        if app_properties:
            body["appProperties"] = app_properties
        if file_id:
            f = self.service.files().update(
                fileId=file_id, body=body, media_body=media, fields="id", supportsAllDrives=True
            ).execute()
        else:
            body["parents"] = [self.folder_id]
            f = self.service.files().create(
                body=body, media_body=media, fields="id", supportsAllDrives=True
            ).execute()
        return f["id"]

    # -- SnapshotStore -----------------------------------------------------
    def load_latest(self):
        from googleapiclient.http import MediaIoBaseDownload

        meta = self._latest_file()
        if meta is None:
            return None
        buf = io.BytesIO()
        request = self.service.files().get_media(fileId=meta["id"], supportsAllDrives=True)
        downloader = MediaIoBaseDownload(buf, request)
        done = False
        while not done:
            _, done = downloader.next_chunk()
        version = int((meta.get("appProperties") or {}).get("version", 0))
        return buf.getvalue(), version

    def remote_version(self):
        meta = self._latest_file()
        if meta is None:
            return None
        return int((meta.get("appProperties") or {}).get("version", 0))

    def save(self, data, version):
        file_id = self._latest_id
        if file_id is None:
            meta = self._latest_file()
            file_id = meta["id"] if meta else None
        self._latest_id = self._upload(self._latest_name, data, file_id, {"version": str(version)})

    def save_daily(self, data, day, keep_days):
        name = f"{self.prefix}_{day}.sqlite"
        existing = self._find(name)
        self._upload(name, data, existing[0]["id"] if existing else None)
        if keep_days <= 0:
            return
        q = (f"'{self.folder_id}' in parents and name contains '{self.prefix}_2' "
             f"and mimeType = '{SNAPSHOT_MIME}' and trashed = false")
        resp = self.service.files().list(
            q=q, fields="files(id, name)", orderBy="name desc", pageSize=1000,
            supportsAllDrives=True, includeItemsFromAllDrives=True,
        ).execute()
        for old in resp.get("files", [])[keep_days:]:
            log.info("Pruning old daily snapshot %s", old["name"])
            self.service.files().delete(fileId=old["id"], supportsAllDrives=True).execute()
