from fastapi import FastAPI, Form
import qrcode
import io
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
import base64
from fastapi.middleware.cors import CORSMiddleware
import os
from dotenv import load_dotenv
from fastapi.openapi.utils import get_openapi
from starlette.staticfiles import StaticFiles
from starlette.concurrency import run_in_threadpool
from contextlib import asynccontextmanager
import logging

from memdb import create_db_from_env

from typing import List
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
from typing import List
from datetime import datetime
import json

# Define IST timezone
IST = timezone(timedelta(hours=5, minutes=30))
load_dotenv()
logging.basicConfig(level=logging.INFO)
# import base64
# import requests
# from googleapiclient.http import MediaIoBaseUpload
# from sendgrid import SendGridAPIClient
# from sendgrid.helpers.mail import Mail

# from fastapi import FastAPI, UploadFile, File, Form
# from db import get_db_connection
# import shutil
# from google.oauth2 import service_account
# from googleapiclient.discovery import build

# from fastapi import UploadFile, File, Form
# from google.oauth2 import service_account
# from googleapiclient.discovery import build
# import json


# Load environment variables from .env file

# In-memory database, restored from Google Drive on startup and backed up on every write.
db = create_db_from_env()


@asynccontextmanager
async def lifespan(app):
    await run_in_threadpool(db.start)  # fails startup if the snapshot can't be restored
    yield
    await run_in_threadpool(db.stop, 20.0)  # final backup on SIGTERM (Render allows 30s)


app = FastAPI(lifespan=lifespan)

FRONT_END_API = os.getenv("FRONT_END_API", "")
SUPPORT_EMAIL = os.getenv("SUPPORT_EMAIL", "")
BACKEND_API = os.getenv("BACKEND_API", "")
THANKYOU_BASENAME = os.getenv("THANKYOU_BASENAME", "")
COMPANY_WEBSITE = os.getenv("COMPANY_WEBSITE", "")

CATALOGUE_URL = f"{BACKEND_API}/files/catalogue.pdf"
MANUAL_URL = f"{BACKEND_API}/files/manual.pdf"

print("FRONT_END_API", FRONT_END_API)
print("BACKEND_API", BACKEND_API)

# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Brevo API Configuration
BREVO_API_KEY = os.getenv("BREVO_API_KEY", "")

print("BREVO_API_KEY", BREVO_API_KEY)

SENDER_EMAIL = os.getenv("SENDER_EMAIL", "")
SENDER_NAME = os.getenv("SENDER_NAME", "")

configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = BREVO_API_KEY
email_api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

app.mount("/files", StaticFiles(directory="service_files"), name="files")


# getting pdfs
@app.get("/get_product_pdfs")
async def get_product_pdfs():
    return {"catalogue_url": CATALOGUE_URL, "manual_url": MANUAL_URL}


# Define response model
class ProductDetail(BaseModel):
    model_name: str
    serial_number: str
    mfg_year: str
    material_url: str
    created_at: str  # Keep as string to avoid datetime formatting issues


@app.get("/get_products", response_model=List[ProductDetail], summary="Fetch Product Details", tags=["Product Details"])
def get_products():
    """Fetch all product details from the database."""
    results = db.query("""
        SELECT model_name, serial_number,mfg_year, material_url, created_at 
        FROM product_details
    """)
    print(len(results))

    products = []
    for row in results:
        model_name, serial_number, mfg_year, material_url, created_at = row
        print(model_name, serial_number, mfg_year, material_url, created_at)
        # Convert created_at from UTC to IST
        if created_at:
            created_at = created_at.replace(tzinfo=timezone.utc).astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')

        products.append({
            "model_name": model_name,
            "serial_number": serial_number,
            "mfg_year": mfg_year,
            "material_url": material_url,
            "created_at": created_at
        })

    return products


# Define response model
class CustomerQuery(BaseModel):
    model_name: str
    serial_number: str
    mfg_year: str
    customer_gmail: str
    customer_city: str
    company_name: str
    created_at: str  # Convert datetime to string


@app.get("/get_customer_queries", response_model=List[CustomerQuery], summary="Fetch Customer Queries",
         tags=["Customer Queries"])
def get_customer_queries():
    """Fetch all customer queries from the database."""
    results = db.query("""
        SELECT model_name, serial_number, mfg_year,customer_gmail, customer_city, company_name, created_at 
        FROM product_queries
    """)

    queries = []
    for row in results:
        model_name, serial_number, mfg_year, customer_gmail, customer_city, company_name, created_at = row

        # Convert MySQL datetime to string format
        created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else None

        queries.append({
            "model_name": model_name,
            "serial_number": serial_number,
            "mfg_year": mfg_year,
            "customer_gmail": customer_gmail,
            "customer_city": customer_city,
            "company_name": company_name,
            "created_at": created_at
        })

    return queries


@app.get("/generate_qr_url", summary="Generate QR Code with URL", tags=["QR Code"])
def generate_qr_url(model_name: str, serial_number: str, mfg_year: str):
    """Generate a QR Code with a URL containing model and serial number."""
    material_url = f"{FRONT_END_API}/form?model={model_name}&serial={serial_number}&mfg_year={mfg_year}"

    # **1️⃣ Check if the entry already exists**
    (count,) = db.query(
        "SELECT COUNT(*) FROM product_details WHERE model_name = ? AND serial_number = ? AND mfg_year = ?",
        (model_name, serial_number, mfg_year),
    )[0]

    if count > 0:
        # **3️⃣ Generate QR Code**
        qr = qrcode.make(material_url)
        buffer = io.BytesIO()
        qr.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        return {"message": "Already exists", "qr_code": f"data:image/png;base64,{qr_base64}", "url": material_url}

    # **2️⃣ Insert if not exists**
    with db.write() as cursor:
        cursor.execute(
            "INSERT INTO product_details (model_name, serial_number, mfg_year, material_url) VALUES (?, ?, ?, ?)",
            (model_name, serial_number, mfg_year, material_url),
        )

    # **3️⃣ Generate QR Code**
    qr = qrcode.make(material_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    return {"qr_code": f"data:image/png;base64,{qr_base64}", "url": material_url}


@app.post("/check_registration", summary="Check if customer is registered", tags=["Customer Queries"])
def check_registration(
        model_name: str = Form(...),
        serial_number: str = Form(...),
        mfg_year: str = Form(...),
        email: str = Form(...)
):
    result = db.query("""
        SELECT EXISTS(
            SELECT 1 FROM product_queries
            WHERE model_name = ? AND serial_number = ? AND mfg_year = ? AND customer_gmail = ?
        ) AS already_exists
    """, (model_name, serial_number, mfg_year, email))[0]
    exists = result[0] == 1
    return {"exists": exists}


@app.post("/submit_form", summary="Submit Form & Send Email", tags=["Form Submission"])
def submit_form(
        email: str = Form(...), company_name: str = Form(...), customer_city: str = Form(...),
        model_name: str = Form(...), serial_number: str = Form(...), mfg_year: str = Form(...)):
    """Submit form and send email using Brevo."""
    # invoice_link = view_invoice(model, serial)
    #
    # pdf_path = download_pdf_from_drive(invoice_link["invoice_url"], model, serial)
    # Send email to user

    with db.write() as cursor:
        cursor.execute(
            """INSERT INTO product_queries
               (model_name, serial_number, mfg_year, customer_gmail, customer_city, company_name)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (model_name, serial_number, mfg_year, email, customer_city, company_name),
        )

    """Send a professional purchase confirmation email to the customer."""

    subject = f"🎉 Thank You for Purchasing {model_name} - Serial: {serial_number} - Mfg Year: {mfg_year}"

    html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #1a73e8;">Thank You for Your Purchase!</h2>
            <p>Dear Customer,</p>
            <p>We appreciate your trust in <b>Our Company</b>. Your purchase of <b>{model_name}</b> with Serial Number <b>{serial_number}</b></b> Manufacturing Year of <b>{mfg_year}</b> has been successfully registered.</p>

            <h3>📘 Product Resources:</h3>
            <ul>
                <li><strong>📄 Product Catalogue:</strong> <a href="{CATALOGUE_URL}" style="color: #1a73e8;">View Catalogue</a></li>
                <li><strong>🛠️ User Manual:</strong> <a href="{MANUAL_URL}" style="color: #1a73e8;">Read Manual</a></li>
            </ul>

            <p>If you have any questions, feel free to contact us on below email {SUPPORT_EMAIL}</p>

            <p>Best Regards,<br><b>{THANKYOU_BASENAME}</b><br>
            <a href="{THANKYOU_BASENAME}" style="color: #1a73e8;"></a>{COMPANY_WEBSITE}</p>
        </body>
        </html>
        """
    send_email(email, subject, html_content)

    # # Notify admin
    # send_email("mayur.chinche2502@gmail.com", "New User Submission",
    #            f"User Info:\nEmail: {email}\nCompany: {company}\nCity: {city}")

    return {"message": "Email Sent", "redirect_url": 'invoice_link'}


# @app.get("/download_pdf/")
# def download_pdf(file_id: str):
#     """Fetches the file from Google Drive and returns it as a PDF response."""
#     drive_url = f"https://drive.google.com/uc?id={file_id}"
#
#     response = requests.get(drive_url, stream=True)
#
#     if response.status_code == 200:
#         return Response(content=response.content, media_type="application/pdf")
#     else:
#         return {"error": "Failed to fetch PDF"}


# def download_pdf_from_drive(drive_url, model, serial):
#     """Download the file from Google Drive and save it as a PDF locally."""
#     try:
#         file_id = drive_url.split("id=")[-1]  # Extract file ID from Google Drive link
#         download_url = f"https://drive.google.com/uc?export=download&id={file_id}"
#
#         response = requests.get(download_url)
#         pdf_path = f"/tmp/{model}_{serial}.pdf"  # Temp storage path
#
#         with open(pdf_path, "wb") as f:
#             f.write(response.content)
#
#         return pdf_path
#     except Exception as e:
#         print(f"Error downloading PDF: {e}")
#         return None

#
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


# def send_email_with_pdf(to_email, subject, body, pdf_path):
#     """Function to send email with PDF attachment using Brevo API"""
#     with open(pdf_path, "rb") as f:
#         pdf_content = base64.b64encode(f.read()).decode()
#
#     email_data = sib_api_v3_sdk.SendSmtpEmail(
#         sender={"email": SENDER_EMAIL, "name": SENDER_NAME},
#         to=[{"email": to_email}],
#         subject=subject,
#         html_content=f"<p>{body}</p>",
#         attachment=[{"content": pdf_content, "name": "Invoice.pdf"}]
#     )
#
#     try:
#         email_api_instance.send_transac_email(email_data)
#         print(f"Email sent successfully to {to_email}")
#     except ApiException as e:
#         print(f"Error sending email: {e}")


# Load credentials
# SERVICE_ACCOUNT_FILE = "config/service_account.json"
# SCOPES = ["https://www.googleapis.com/auth/drive.file"]
#
# credentials = service_account.Credentials.from_service_account_file(
#     SERVICE_ACCOUNT_FILE, scopes=SCOPES
# )
# drive_service = build("drive", "v3", credentials=credentials)
#
# FOLDER_ID = "1YjNGzelrs2Z-z2QrHkt1pcYngknoUlNh"
#
# from googleapiclient.http import MediaIoBaseUpload
# import io
#
#
# @app.post("/upload_invoice")
# async def upload_invoice(model_name: str = Form(...), serial_number: str = Form(...), file: UploadFile = File(...)):
#     """Upload invoice to Google Drive and return URL."""
#     try:
#         file_name = f"{model_name}_{serial_number}.pdf"
#
#         # Read file content
#         file_bytes = await file.read()
#         media = MediaIoBaseUpload(io.BytesIO(file_bytes), mimetype="application/pdf")
#
#         # Debugging: Print folder ID before making request
#         print(f"Uploading to Folder ID: {FOLDER_ID}")
#         print(file_name)
#         # Upload to Google Drive
#         file_metadata = {"name": file_name, "parents": [FOLDER_ID]}
#         uploaded_file = drive_service.files().create(
#             body=file_metadata, media_body=media, fields="id"
#         ).execute()
#         print(uploaded_file)
#         file_id = uploaded_file["id"]
#         invoice_url = f"https://drive.google.com/uc?id={file_id}"
#         # Store invoice URL in database
#         connection = get_db_connection()
#         cursor = connection.cursor()
#         insert_query = """
#             INSERT INTO product_documents (model_name, serial_number, invoice_url)
#             VALUES (%s, %s, %s)
#             """
#         cursor.execute(insert_query, (model_name, serial_number, invoice_url))
#         connection.commit()
#         cursor.close()
#         connection.close()
#
#         return {"message": "Invoice uploaded successfully", "invoice_url": invoice_url}
#
#     except Exception as e:
#         return {"error": str(e)}
#
#
# @app.get("/view_invoice")
# def view_invoice(model_name: str, serial_number: str):
#     """Fetch invoice URL from DB and return it."""
#     connection = get_db_connection()
#     cursor = connection.cursor()
#     select_query = """
#     SELECT invoice_url FROM product_documents WHERE model_name=%s AND serial_number=%s
#     """
#     cursor.execute(select_query, (model_name, serial_number))
#     result = cursor.fetchone()
#     cursor.close()
#     connection.close()
#
#     if not result:
#         return {"error": "Invoice not found"}
#
#     return {"invoice_url": result[0]}


@app.get("/health/db", summary="In-memory database backup status", tags=["Health"])
def health_db():
    """503 when writes are waiting on a failing backup, so Render/uptime monitors can alert."""
    status = db.status()
    if status["unsaved_writes"] and status["consecutive_failures"]:
        raise HTTPException(status_code=503, detail=status)
    return status


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_openapi(title="QR Code API", version="1.0.0", routes=app.routes)
