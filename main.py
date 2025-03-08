from fastapi import FastAPI, Form
import qrcode
import io
import base64
import os
import requests
from googleapiclient.http import MediaIoBaseUpload
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi
from fastapi import FastAPI, UploadFile, File, Form
from db import get_db_connection
import shutil
from google.oauth2 import service_account
from googleapiclient.discovery import build
from fastapi import FastAPI, UploadFile, File, Form
from google.oauth2 import service_account
from googleapiclient.discovery import build
import json
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import base64
from fastapi.middleware.cors import CORSMiddleware

load_dotenv()

app = FastAPI()

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Update if needed
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Brevo API Configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY")
SENDER_EMAIL = "mayur.chinche2502@gmail.com"
SENDER_NAME = "Mayur Chinche"

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY
email_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))


@app.get("/generate_qr", summary="Generate QR Code", tags=["QR Code"])
def generate_qr(model_name: str, serial_number: str):
    """Generate a QR Code with a URL containing model and serial number."""
    url = f"https://yourfrontend.com/form?model={model_name}&serial={serial_number}"
    qr = qrcode.make(url)

    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {"qr_code": f"data:image/png;base64,{qr_base64}", "url": url}


@app.post("/submit_form", summary="Submit Form & Send Email", tags=["Form Submission"])
def submit_form(
        email: str = Form(...), company: str = Form(...), city: str = Form(...),
        model: str = Form(...), serial: str = Form(...)):
    """Submit form and send email using Brevo."""
    invoice_link = view_invoice(model, serial)

    pdf_path = download_pdf_from_drive(invoice_link["invoice_url"], model, serial)
    # Send email to user
    send_email_with_pdf(email, f"Product Details {model}: {serial}",
                        "Please find the attached invoice PDF.", pdf_path)

    # Notify admin
    send_email("mayur.chinche2502@gmail.com", "New User Submission",
               f"User Info:\nEmail: {email}\nCompany: {company}\nCity: {city}")

    return {"message": "Email Sent", "redirect_url": invoice_link}


@app.get("/download_pdf/")
def download_pdf(file_id: str):
    """Fetches the file from Google Drive and returns it as a PDF response."""
    drive_url = f"https://drive.google.com/uc?id={file_id}"

    response = requests.get(drive_url, stream=True)

    if response.status_code == 200:
        return Response(content=response.content, media_type="application/pdf")
    else:
        return {"error": "Failed to fetch PDF"}


def download_pdf_from_drive(drive_url, model, serial):
    """Download the file from Google Drive and save it as a PDF locally."""
    try:
        file_id = drive_url.split("id=")[-1]  # Extract file ID from Google Drive link
        download_url = f"https://drive.google.com/uc?export=download&id={file_id}"

        response = requests.get(download_url)
        pdf_path = f"/tmp/{model}_{serial}.pdf"  # Temp storage path

        with open(pdf_path, "wb") as f:
            f.write(response.content)

        return pdf_path
    except Exception as e:
        print(f"Error downloading PDF: {e}")
        return None


def send_email(to_email, subject, body):
    """Function to send email using Brevo API"""
    email_data = sib_api_v3_sdk.SendSmtpEmail(
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        to=[{"email": to_email}],
        subject=subject,
        html_content=f"<p>{body}</p>"
    )

    try:
        email_api_instance.send_transac_email(email_data)
        print(f"Email sent successfully to {to_email}")
    except ApiException as e:
        print(f"Error sending email: {e}")


def send_email_with_pdf(to_email, subject, body, pdf_path):
    """Function to send email with PDF attachment using Brevo API"""
    with open(pdf_path, "rb") as f:
        pdf_content = base64.b64encode(f.read()).decode()

    email_data = sib_api_v3_sdk.SendSmtpEmail(
        sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
        to=[{"email": to_email}],
        subject=subject,
        html_content=f"<p>{body}</p>",
        attachment=[{"content": pdf_content, "name": "Invoice.pdf"}]
    )

    try:
        email_api_instance.send_transac_email(email_data)
        print(f"Email sent successfully to {to_email}")
    except ApiException as e:
        print(f"Error sending email: {e}")


# Load credentials
SERVICE_ACCOUNT_FILE = "config/service_account.json"
SCOPES = ["https://www.googleapis.com/auth/drive.file"]

credentials = service_account.Credentials.from_service_account_file(
    SERVICE_ACCOUNT_FILE, scopes=SCOPES
)
drive_service = build("drive", "v3", credentials=credentials)

FOLDER_ID = "1YjNGzelrs2Z-z2QrHkt1pcYngknoUlNh"

from googleapiclient.http import MediaIoBaseUpload
import io


@app.post("/upload_invoice")
async def upload_invoice(model_name: str = Form(...), serial_number: str = Form(...), file: UploadFile = File(...)):
    """Upload invoice to Google Drive and return URL."""
    try:
        file_name = f"{model_name}_{serial_number}.pdf"

        # Read file content
        file_bytes = await file.read()
        media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype="application/pdf")

        # Debugging: Print folder ID before making request
        print(f"Uploading to Folder ID: {FOLDER_ID}")
        print(file_name)
        # Upload to Google Drive
        file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
        uploaded_file = drive_service.files().create(
            body=file_metadata, media_body=media, fields="id"
        ).execute()
        print(uploaded_file)
        file_id = uploaded_file["id"]
        invoice_url = f"https://drive.google.com/uc?id={file_id}"
        # Store invoice URL in database
        connection = get_db_connection()
        cursor = connection.cursor()
        insert_query = """
            INSERT INTO product_documents (model_name, serial_number, invoice_url)
            VALUES (%s, %s, %s)
            """
        cursor.execute(insert_query, (model_name, serial_number, invoice_url))
        connection.commit()
        cursor.close()
        connection.close()

        return {"message": "Invoice uploaded successfully", "invoice_url": invoice_url}

    except Exception as e:
        return {"error": str(e)}


@app.get("/view_invoice")
def view_invoice(model_name: str, serial_number: str):
    """Fetch invoice URL from DB and return it."""
    connection = get_db_connection()
    cursor = connection.cursor()
    select_query = """
    SELECT invoice_url FROM product_documents WHERE model_name=%s AND serial_number=%s
    """
    cursor.execute(select_query, (model_name, serial_number))
    result = cursor.fetchone()
    cursor.close()
    connection.close()

    if not result:
        return {"error": "Invoice not found"}

    return {"invoice_url": result[0]}


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_openapi(title="QR Code API", version="1.0.0", routes=app.routes)
