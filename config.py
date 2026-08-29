from dotenv import load_dotenv
import os

load_dotenv()


class Config:
    db_host = os.getenv("DB_HOST")
    db_port = os.getenv("DB_PORT")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD")
    db_name = os.getenv("DB_NAME")

    from_email = os.getenv("FROM_EMAIL")
    email_app_password = os.getenv("EMAIL_APP_PASSWORD")
    


class EmailTemplates:

    @staticmethod
    def send_otp_template(otp: int, username: str):
        template = f"""
                    Hello {username},

                    Your One-Time Password (OTP) is: {otp}

                    ⚠️ Please note: This code is valid for 5 minutes only.
                    Do not share this OTP with anyone for security reasons.

                    Regards,
                    SNS Team
                    """
        return template

    @staticmethod
    def send_reset_password_template(username: str, link: str, time: int):
        template = f"""
                    Hello {username},

                    We received a request to reset your account password.

                    To proceed, please click the link below:

                    👉 Reset URL: {link}

                    ⚠️ This link will remain valid for {time} minutes only.

                    If you did not request a password reset, please ignore this email.

                    For your security, do not share this link with anyone.

                    Regards,
                    SNS Team
                    """
        return template

