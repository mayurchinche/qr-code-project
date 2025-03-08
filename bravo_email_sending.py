import sib_api_v3_sdk
from sib_api_v3_sdk.rest import ApiException

# Setup API client
configuration = sib_api_v3_sdk.Configuration()
configuration.api_key[
    'api-key'] = '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'

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
    print("Email sent successfully!")
except ApiException as e:
    print(f"Error: {e}")
