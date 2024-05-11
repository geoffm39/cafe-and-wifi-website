import smtplib
import os

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_EMAIL_PASSWORD = os.environ.get('ADMIN_EMAIL_PASSWORD')
SMTP_SERVER = os.environ.get('SMTP_SERVER')


def send_email(name, email, subject, message):
    with smtplib.SMTP(SMTP_SERVER, port=587) as connection:
        connection.starttls()
        connection.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
        connection.sendmail(from_addr=ADMIN_EMAIL,
                            to_addrs=email,
                            msg=f"Subject:Portfolio Message\n\nName: {name}\nEmail: {email}\nSubject: {subject}\n{message}")