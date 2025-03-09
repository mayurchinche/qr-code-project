import os
import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get API key securely
api_key = os.getenv("BREVO_API_KEY")
print("Loaded Env Vars:", api_key)
# Setup API client
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key['api-key'] = api_key

# Create an API instance
api_instance = sib_api_v3_sdk.TransactionalEmailsApi(sib_api_v3_sdk.ApiClient(configuration))

# Email details
email = sib_api_v3_sdk.SendSmtpEmail(
    to=[{"email": "mayur.chinche1999@gmail.com", "name": "Mayur Chinche"}],
    sender={"email": "mayur.chinche2502@gmail.com", "name": "Mayur Chinche"},
    subject="Test Email from Brevo",
    html_content="<p>Hello, this is a test email from Brevo!</p>"
)

# Send email
try:
    api_instance.send_transac_email(email)
    print("✅ Email sent successfully!")
except ApiException as e:
    print(f"❌ Error: {e}")
