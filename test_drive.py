from google.oauth2 import service_account
from googleapiclient.discovery import build

# Load credentials
SERVICE_ACCOUNT_FILE = "credentials.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

try:
    credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES
    )
    drive_service = build("drive", "v3", credentials=credentials)
    print("✅ Google Drive API Authentication Successful!")
except Exception as e:
    print(f"❌ Authentication Failed: {e}")
