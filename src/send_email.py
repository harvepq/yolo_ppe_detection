import smtplib

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from config import EMAIL_PASSWORD, EMAIL_FROM, EMAIL_TO

# Email credentials
password = EMAIL_PASSWORD
from_email = EMAIL_FROM
to_email = EMAIL_TO

server = smtplib.SMTP("smtp.gmail.com: 587")
server.starttls()
server.login(from_email, password)

def send_email(to_email, from_email, object_detected=1):
    """Sends an email notification indicating the number of objects detected; defaults to 1 object."""
    message = MIMEMultipart()
    message["From"] = from_email
    message["To"] = to_email
    message["Subject"] = "Security Alert"
    # Add in the message body
    message_body = f"ALERT - {object_detected} objects has been detected!!"

    message.attach(MIMEText(message_body, "plain"))
    server.sendmail(from_email, to_email, message.as_string())


send_email(to_email=to_email, from_email=from_email)

server.quit()