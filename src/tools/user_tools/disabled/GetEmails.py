import imaplib
import email
import os

__all__ = ['GetEmails']

class GetEmails:
    dependencies = ['os']

    inputSchema = {
        "name": "GetEmails",
        "description": "Reads emails from an IMAP server.",
        "parameters": {
            "type": "object",
            "properties": {
                "num_emails": {
                    "type": "integer",
                    "description": "Number of emails to retrieve (default: 5).",
                    "default": 5
                }
            },
            "required": []
        }
    }

    def __init__(self):
        # Replace with your actual email provider's IMAP server address
        self.imap_server = "imap.gmail.com"  # e.g., imap.gmail.com
        self.email_address = os.environ.get("EMAIL_ADDRESS")  # Replace with your email address
        self.password = os.environ.get("EMAIL_PASSWORD")  # Replace with your password or app password

    def run(self, **kwargs):
        num_emails = kwargs.get("num_emails", 5)

        try:
            # Connect to the IMAP server
            mail = imaplib.IMAP4_SSL(self.imap_server)
            mail.login(self.email_address, self.password)
            mail.select("inbox")  # You can select other mailboxes like "sent"

            # Search for emails (ALL = all emails, or use specific criteria)
            result, data = mail.search(None, "ALL")
            mail_ids = data[0].split()

            # Get the most recent emails
            recent_emails = mail_ids[-num_emails:]

            email_messages = []
            for num in recent_emails:
                result, msg_data = mail.fetch(num, '(RFC822)')
                raw_email = msg_data[0][1]
                msg = email.message_from_bytes(raw_email)

                # Decode email headers and body
                try:
                    subject = email.header.decode_header(msg["Subject"])[0][0]
                    if isinstance(subject, bytes):
                        subject = subject.decode()
                except:
                    subject = "No Subject"

                try:
                    from_ = email.header.decode_header(msg.get("From"))[0][0]
                    if isinstance(from_, bytes):
                        from_ = from_.decode()
                except:
                    from_ = "Unknown Sender"

                # Extract the body of the email
                body = ""  # Initialize body to an empty string
                if msg.is_multipart():
                    for part in msg.walk():
                        ctype = part.get_content_type()
                        cdispo = str(part.get("Content-Disposition"))

                        if ctype == "text/plain" and "attachment" not in cdispo:
                            body = part.get_payload(decode=True).decode()
                            break
                else:
                    body = msg.get_payload(decode=True).decode()

                email_messages.append({
                    "subject": subject,
                    "from": from_,
                    "body": body
                })

            mail.close()
            mail.logout()

            return {
                "status": "success",
                "message": "Emails retrieved successfully.",
                "output": email_messages
            }

        except Exception as e:
            return {
                "status": "error",
                "message": f"An error occurred: {str(e)}",
                "output": None
            }
