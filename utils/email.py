import smtplib
import os

ADMIN_EMAIL = os.environ.get('ADMIN_EMAIL')
ADMIN_EMAIL_PASSWORD = os.environ.get('ADMIN_EMAIL_PASSWORD')
SMTP_SERVER = os.environ.get('SMTP_SERVER')


def send_email(email, subject, message):
    with smtplib.SMTP(SMTP_SERVER, port=587) as connection:
        connection.starttls()
        connection.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
        connection.sendmail(from_addr=ADMIN_EMAIL,
                            to_addrs=email,
                            msg=f"Subject:{subject}\n\n{message}")


def receive_email(subject, message):
    with smtplib.SMTP(SMTP_SERVER, port=587) as connection:
        connection.starttls()
        connection.login(ADMIN_EMAIL, ADMIN_EMAIL_PASSWORD)
        connection.sendmail(from_addr=ADMIN_EMAIL,
                            to_addrs=ADMIN_EMAIL,
                            msg=f"Subject:{subject}\n\n{message}")
