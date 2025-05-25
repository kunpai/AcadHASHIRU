import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os

__all__ = ['SendEmails']

class SendEmails:
    dependencies = ['os']

    inputSchema = {
        "name": "SendEmails",
        "description": "Writes and sends an email.",
        "parameters": {
            "type": "object",
            "properties": {
                "receiver_email": {
                    "type": "string",
                    "description": "The recipient's email address.",
                },
                "subject": {
                    "type": "string",
                    "description": "The email subject.",
                },
                "body": {
                    "type": "string",
                    "description": "The email body.",
                },
            },
            "required": ["receiver_email", "subject", "body"],
        }
    }

    def __init__(self):
        self.sender_email = os.environ.get("EMAIL_ADDRESS")
        self.sender_password = os.environ.get("EMAIL_PASSWORD")

    def run(self, **kwargs):
        receiver_email = kwargs["receiver_email"]
        subject = kwargs["subject"]
        body = kwargs["body"]

        try:
            msg = MIMEMultipart()
            msg['From'] = self.sender_email
            msg['To'] = receiver_email
            msg['Subject'] = subject

            msg.attach(MIMEText(body, 'plain'))

            server = smtplib.SMTP('smtp.gmail.com', 587)
            server.starttls()
            server.login(self.sender_email, self.sender_password)
            text = msg.as_string()
            server.sendmail(self.sender_email, receiver_email, text)
            server.quit()

            return {"status": "success", "message": "Email sent successfully!"}

        except Exception as e:
            return {"status": "error", "message": str(e)}
