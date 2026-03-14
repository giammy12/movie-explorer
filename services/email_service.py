import smtplib
from email.mime.text import MIMEText
from config import SMTP_FROM, SMTP_HOST, SMTP_PASSWORD, SMTP_PORT, SMTP_USERNAME

def send_reset_email(recipient_email, reset_link):
    subject = "Reset password - Movie Explorer"

    body = f"""
Ciao,

Abbiamo ricevuto una richiesta di reset della password per il tuo account Movie Explorer.

Clicca il link qui sotto per impostare una nuova password:

{reset_link}

Se non hai richiesto tu questa operazione, puoi ignorare questa email.
"""

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = recipient_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, recipient_email, message.as_string())


def send_otp_email(recipient_email, otp_code, purpose):
    if purpose == "change_password":
        subject = "Codice OTP cambio password - Movie Explorer"
        action_text = "cambiare la password"
    elif purpose == "delete_account":
        subject = "Codice OTP eliminazione account - Movie Explorer"
        action_text = "eliminare il tuo account"
    else:
        subject = "Codice OTP - Movie Explorer"
        action_text = "completare l'operazione"

    body = f"""
Ciao,

Hai richiesto un codice OTP per {action_text} su Movie Explorer.

Il tuo codice OTP è:

{otp_code}

Il codice scadrà tra 10 minuti.

Se non hai richiesto tu questa operazione, ignora questa email.
"""

    message = MIMEText(body)
    message["Subject"] = subject
    message["From"] = SMTP_FROM
    message["To"] = recipient_email

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.starttls()
        server.login(SMTP_USERNAME, SMTP_PASSWORD)
        server.sendmail(SMTP_FROM, recipient_email, message.as_string())