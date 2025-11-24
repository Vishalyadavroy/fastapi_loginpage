# # app/email_utils.py

# import smtplib
# from email.mime.text import MIMEText
# from email.mime.multipart import MIMEMultipart
# import os
# from dotenv import load_dotenv

# # Load environment variables from .env file
# load_dotenv()

# # --- Configuration ---
# # Read credentials from the environment variables
# SENDER_EMAIL = os.getenv("SMTP_SENDER_EMAIL")
# SENDER_PASSWORD = os.getenv("SMTP_SENDER_PASSWORD") # This must be the App Password

# SMTP_SERVER = "smtp.gmail.com"
# SMTP_PORT = 587 # Use 587 for TLS (STARTTLS)

# def send_email(to_email: str, subject: str, body: str):
#     if not SENDER_EMAIL or not SENDER_PASSWORD:
#         print("ERROR: Email credentials not set in .env file.")
#         return

#     message = MIMEMultipart()
#     message["From"] = SENDER_EMAIL
#     message["To"] = to_email
#     message["Subject"] = subject
    
#     # Attach the email body
#     message.attach(MIMEText(body, "plain"))

#     try:
#         # Connect to the SMTP server using TLS
#         with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
#             server.ehlo() # Can be used to identify yourself to the server
#             server.starttls() # Secure the connection
#             server.ehlo() # Re-identify after starting TLS
            
#             # 👇 The failing line, now using environment variables
#             server.login(SENDER_EMAIL, SENDER_PASSWORD) 
            
#             server.sendmail(SENDER_EMAIL, to_email, message.as_string())
#             print(f"SUCCESS: Reset password email sent to {to_email}")
            
#     except smtplib.SMTPAuthenticationError:
#         print("SMTP ERROR: Authentication failed. Check your App Password and email address.")
#         raise
#     except Exception as e:
#         print(f"An error occurred while sending email: {e}")
#         raise



#     # phkt rksm rzqs iwxl


# app/email_utils.py

import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# --- Configuration ---
SENDER_EMAIL = os.getenv("SMTP_SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SMTP_SENDER_PASSWORD")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

def send_email(to_email: str, subject: str, body: str):
    # -------------------- 👇 DEBUGGING STEP 1: Check Credentials --------------------
    print("\n--- DEBUG: Checking SMTP Credentials ---")
    print(f"SENDER_EMAIL: {SENDER_EMAIL}")
    # Print only the length of the password, NOT the password itself, for security!
    print(f"SENDER_PASSWORD Length: {len(SENDER_PASSWORD) if SENDER_PASSWORD else 0}")
    print("-----------------------------------------")
    # ---------------------------------------------------------------------------------
    
    if not SENDER_EMAIL or not SENDER_PASSWORD:
        print("ERROR: Email credentials not set in .env file.")
        return

    message = MIMEMultipart()
    message["From"] = SENDER_EMAIL
    message["To"] = to_email
    message["Subject"] = subject
    
    # -------------------- 👇 DEBUGGING STEP 2: Check Email Body Content --------------------
    print(f"--- DEBUG: Email Content Check ---")
    print(f"To: {to_email}")
    print(f"Subject: {subject}")
    # Print the start of the body to verify the reset link/token is included
    print(f"Body snippet (first 100 chars): {body[:100]}")
    print("------------------------------------")
    # -----------------------------------------------------------------------------------------

    # Attach the email body
    message.attach(MIMEText(body, "plain"))

    try:
        # Connect to the SMTP server using TLS
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.ehlo()
            server.starttls()
            server.ehlo()
            
            server.login(SENDER_EMAIL, SENDER_PASSWORD) 
            
            server.sendmail(SENDER_EMAIL, to_email, message.as_string())
            print(f"SUCCESS: Reset password email sent to {to_email}")
            
    except smtplib.SMTPAuthenticationError:
        print("SMTP ERROR: Authentication failed. Check your App Password (spaces removed!) and email address.")
        raise
    except Exception as e:
        print(f"An error occurred while sending email: {e}")
        raise