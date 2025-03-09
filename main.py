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

from create_tables import create_tables
from db import get_db_connection

from typing import List
from pydantic import BaseModel
from datetime import datetime, timezone, timedelta

# Define IST timezone
IST = timezone(timedelta(hours=5, minutes=30))
load_dotenv()
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

create_tables()

app = FastAPI()

front_end_api = os.getenv("FRONT_END_API", "")
catalogue_url = os.getenv("CATALOGUE_URL", "")
manual_url = os.getenv("MANUAL_URL", "")
# Enable CORS for React frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=[front_end_api],  # Update if needed
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


# Define response model
class ProductDetail(BaseModel):
    model_name: str
    serial_number: str
    material_url: str
    created_at: str  # Keep as string to avoid datetime formatting issues


@app.get("/get_products", response_model=List[ProductDetail], summary="Fetch Product Details", tags=["Product Details"])
def get_products():
    """Fetch all product details from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT model_name, serial_number, material_url, created_at 
        FROM product_details
    """
    cursor.execute(query)
    results = cursor.fetchall()
    print(len(results))
    cursor.close()
    connection.close()

    products = []
    for row in results:
        model_name, serial_number, material_url, created_at = row
        print(model_name, serial_number, material_url, created_at)
        # Convert created_at from UTC to IST
        if created_at:
            created_at = created_at.replace(tzinfo=timezone.utc).astimezone(IST).strftime('%Y-%m-%d %H:%M:%S')

        products.append({
            "model_name": model_name,
            "serial_number": serial_number,
            "material_url": material_url,
            "created_at": created_at
        })

    return products


# Define response model
class CustomerQuery(BaseModel):
    model_name: str
    serial_number: str
    customer_gmail: str
    customer_city: str
    company_name: str
    created_at: str  # Convert datetime to string


@app.get("/get_customer_queries", response_model=List[CustomerQuery], summary="Fetch Customer Queries",
         tags=["Customer Queries"])
def get_customer_queries():
    """Fetch all customer queries from the database."""
    connection = get_db_connection()
    cursor = connection.cursor()

    query = """
        SELECT model_name, serial_number, customer_gmail, customer_city, company_name, created_at 
        FROM product_queries
    """
    cursor.execute(query)
    results = cursor.fetchall()
    cursor.close()
    connection.close()

    queries = []
    for row in results:
        model_name, serial_number, customer_gmail, customer_city, company_name, created_at = row

        # Convert MySQL datetime to string format
        created_at = created_at.strftime('%Y-%m-%d %H:%M:%S') if created_at else None

        queries.append({
            "model_name": model_name,
            "serial_number": serial_number,
            "customer_gmail": customer_gmail,
            "customer_city": customer_city,
            "company_name": company_name,
            "created_at": created_at
        })

    return queries


@app.get("/generate_qr_url", summary="Generate QR Code with URL", tags=["QR Code"])
def generate_qr_url(model_name: str, serial_number: str):
    """Generate a QR Code with a URL containing model and serial number."""
    material_url = f"{front_end_api}/form?model={model_name}&serial={serial_number}"

    connection = get_db_connection()
    cursor = connection.cursor()

    # **1️⃣ Check if the entry already exists**
    check_query = """
        SELECT COUNT(*) FROM product_details WHERE model_name = %s AND serial_number = %s
    """
    cursor.execute(check_query, (model_name, serial_number))
    (count,) = cursor.fetchone()

    if count > 0:
        cursor.close()
        connection.close()
        return {"message": "Already exists", "url": material_url}

    # **2️⃣ Insert if not exists**
    insert_query = """
        INSERT INTO product_details (model_name, serial_number, material_url)
        VALUES (%s, %s, %s)
    """
    cursor.execute(insert_query, (model_name, serial_number, material_url))
    connection.commit()

    # **3️⃣ Generate QR Code**
    qr = qrcode.make(material_url)
    buffer = io.BytesIO()
    qr.save(buffer, format="PNG")
    qr_base64 = base64.b64encode(buffer.getvalue()).decode()

    cursor.close()
    connection.close()

    return {"qr_code": f"data:image/png;base64,{qr_base64}", "url": material_url}


@app.post("/submit_form", summary="Submit Form & Send Email", tags=["Form Submission"])
def submit_form(
        email: str = Form(...), company_name: str = Form(...), customer_city: str = Form(...),
        model_name: str = Form(...), serial_number: str = Form(...)):
    """Submit form and send email using Brevo."""
    # invoice_link = view_invoice(model, serial)
    #
    # pdf_path = download_pdf_from_drive(invoice_link["invoice_url"], model, serial)
    # Send email to user

    connection = get_db_connection()
    cursor = connection.cursor()
    insert_query = """
                INSERT INTO product_queries (model_name, serial_number, customer_gmail,customer_city,company_name)
                VALUES (%s, %s, %s,%s, %s)
                """
    cursor.execute(insert_query, (model_name, serial_number, email, customer_city, company_name))
    connection.commit()
    cursor.close()
    connection.close()

    """Send a professional purchase confirmation email to the customer."""

    subject = f"🎉 Thank You for Purchasing {model_name} - Serial: {serial_number}"

    html_content = f"""
        <html>
        <body style="font-family: Arial, sans-serif; line-height: 1.6; color: #333;">
            <h2 style="color: #1a73e8;">Thank You for Your Purchase!</h2>
            <p>Dear Customer,</p>
            <p>We appreciate your trust in <b>Our Company</b>. Your purchase of <b>{model_name}</b> with Serial Number <b>{serial_number}</b> has been successfully registered.</p>

            <h3>📘 Product Resources:</h3>
            <ul>
                <li><strong>📄 Product Catalogue:</strong> <a href="{catalogue_url}" style="color: #1a73e8;">View Catalogue</a></li>
                <li><strong>🛠️ User Manual:</strong> <a href="{manual_url}" style="color: #1a73e8;">Read Manual</a></li>
            </ul>

            <p>If you have any questions, feel free to <a href="mailto:support@yourcompany.com" style="color: #1a73e8;">contact us</a>.</p>

            <p>Best Regards,<br><b>Your Company Name</b><br>
            <a href="https://yourcompany.com" style="color: #1a73e8;">www.yourcompany.com</a></p>
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


@app.get("/docs", include_in_schema=False)
def custom_swagger_ui_html():
    return get_openapi(title="QR Code API", version="1.0.0", routes=app.routes)
