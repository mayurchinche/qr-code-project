import os
import glob
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

SERVICE_ACCOUNT_FILE = "credentials.json"
FOLDER_ID = "1YzL4tmgyfLOYbzLntlp8yoXBjG2nmbZH"
# Load service account credentials
creds = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE,
    scopes=['https://www.googleapis.com/auth/drive']
)

# Initialize Google Drive API
service = build('drive', 'v3', credentials=creds)

# Find latest SQL backup file from local folder
backup_files = sorted(glob.glob('backups/*.sql'), key=os.path.getmtime, reverse=True)
if not backup_files:
    raise Exception("No backup file found to upload.")
latest_backup = backup_files[0]
latest_backup_name = os.path.basename(latest_backup)

KEEP_BACKUPS = int(os.getenv("KEEP_BACKUPS", "14"))

# Upload the latest backup first, so a failed upload never leaves Drive without backups
file_metadata = {
    'name': latest_backup_name,
    'parents': [FOLDER_ID]
}
media = MediaFileUpload(latest_backup, mimetype='application/sql')
file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
print(f"Backup uploaded to Google Drive. File ID: {file.get('id')}")

# Keep only the newest KEEP_BACKUPS .sql files in the Drive folder
query = f"'{FOLDER_ID}' in parents and mimeType='application/sql' and trashed=false"
results = service.files().list(
    q=query, fields="files(id, name, createdTime)", orderBy="createdTime desc", pageSize=1000
).execute()
files = results.get('files', [])

for old in files[KEEP_BACKUPS:]:
    print(f"Deleting old backup: {old['name']} (ID: {old['id']})")
    service.files().delete(fileId=old['id']).execute()
