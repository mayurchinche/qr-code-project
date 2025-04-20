from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseUpload
import io

# Load credentials
SERVICE_ACCOUNT_FILE = "config/service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

# Verify folder access
FOLDER_ID = "1YzL4tmgyfLOYbzLntlp8yoXBjG2nmbZH"
try:
    results = drive_service.files().list(q=f"'{FOLDER_ID}' in parents", fields="files(id, name)").execute()
    files = results.get("files", [])
    if files:
        print("✅ Service Account can access the folder!")

    else:
        print("✅ Service Account has access, but the folder is empty.")

        file_name = "test_upload.pdf"
        file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
        media = MediaIoBaseUpload(io.BytesIO(b"Test file content"), mimetype="application/pdf")
        print("Uploading the file {}".format(file_name))

        results = drive_service.files().list(q="mimeType='application/vnd.google-apps.folder'",
                                             fields="files(id, name)").execute()
        print("Folders:", results)
        for folder in results.get("files", []):
            print(f"Folder: {folder['name']} (ID: {folder['id']})")

        uploaded_file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()

        print(f"✅ File uploaded successfully! File ID: {uploaded_file['id']}")
        for file in files:
            print(f"File: {file['name']} (ID: {file['id']})")

except Exception as e:
    print(f"❌ Error: {e}")
