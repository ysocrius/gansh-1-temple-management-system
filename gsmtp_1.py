import smtplib
import getpass
from email.mime.text import MIMEText

MAIL_SERVER = "smtp.gmail.com"
MAIL_PORT = 587
MAIL_USERNAME = "yeshwanthcr108@gmail.com"
MAIL_PASSWORD = "vbqcptpnblofsvuj"
MAIL_DEFAULT_SENDER = MAIL_USERNAME
MAIL_RECEIVER = "yeshbuz7@gmail.com"

def send_email():
    msg = MIMEText("This is a test email from Python!")  
    msg["Subject"] = "Test Email"
    msg["From"] = MAIL_DEFAULT_SENDER
    msg["To"] = MAIL_RECEIVER

    try:
        with smtplib.SMTP(MAIL_SERVER, MAIL_PORT) as server:
            print("Connecting to server...")
            server.starttls()
            print("Starting TLS...")
            server.login(MAIL_USERNAME, MAIL_PASSWORD)
            print(f"Logged in as {MAIL_USERNAME}")
            server.sendmail(MAIL_DEFAULT_SENDER, MAIL_RECEIVER, msg.as_string())
            print(f"Email sent from {MAIL_DEFAULT_SENDER} to {MAIL_RECEIVER}")
        print("✅ Email sent successfully!")
    except smtplib.SMTPAuthenticationError:
        print("❌ Authentication failed. Check your username and app password.")
        print("   Make sure you're using an App Password if you have 2FA enabled.")
    except smtplib.SMTPException as e:
        print(f"❌ SMTP error: {e}")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    choice = input("Type 'yes' to send an email: ").strip().lower()
    if choice == "yes":
        send_email()
    else:
        print("Email not sent.")
