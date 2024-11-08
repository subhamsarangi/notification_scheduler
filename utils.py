import os
import traceback
import logging
from functools import wraps
import asyncio
import socket
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

import aiosmtplib
from flask import jsonify
from werkzeug.exceptions import NotFound, UnsupportedMediaType


smtp_details = {
    "server": os.environ.get("SMTP_SERVER"),
    "port": int(os.environ.get("SMTP_PORT")),
    "username": os.environ.get("SMTP_USERNAME"),
    "password": os.environ.get("SMTP_PASSWORD"),
}

def handle_exceptions(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except NotFound:
            return jsonify(
                {"message": "requested resource not found", "status": "error"}
            )
        except UnsupportedMediaType:
            return jsonify(
                {"message": "request media is not supported", "status": "error"}
            )
        except Exception as e:
            logging.error(traceback.format_exc())
            return jsonify({"error": "An unexpected error occurred."}), 500

    return decorated_function


def check_smtp(smtp_details):
    timeout = 10
    try:
        if smtp_details["port"] == 465:
            with smtplib.SMTP_SSL(
                smtp_details["server"], smtp_details["port"], timeout=timeout
            ) as server:
                server.login(smtp_details["username"], smtp_details["password"])
        else:
            with smtplib.SMTP(
                smtp_details["server"], smtp_details["port"], timeout=timeout
            ) as server:
                server.starttls()
                server.login(smtp_details["username"], smtp_details["password"])

        return {"status": "success", "message": "SMTP connection successful!"}
    except smtplib.SMTPAuthenticationError:
        return {
            "status": "error",
            "message": "Authentication failed. Check your username and password.",
        }
    except smtplib.SMTPConnectError:
        return {
            "status": "error",
            "message": "Connection failed. Check the SMTP server and port.",
        }
    except socket.timeout:
        return {
            "status": "error",
            "message": "Connection timed out. The server may not be reachable.",
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"status": "error", "message": str(e)}


def send_email(smtp_details, email_subject, email_body, recipients, cc=None):
    try:
        timeout = 5
        msg = MIMEMultipart()
        msg["From"] = smtp_details["username"]
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = email_subject

        if cc:
            msg["Cc"] = ", ".join(cc)
            recipients += cc

        print(recipients, "*****************************")
        msg.attach(MIMEText(email_body, "html"))
        if smtp_details["port"] == 465:
            with smtplib.SMTP_SSL(
                smtp_details["server"], smtp_details["port"], timeout=timeout
            ) as server:
                server.login(smtp_details["username"], smtp_details["password"])
                server.sendmail(smtp_details["username"], recipients, msg.as_string())
        else:
            with smtplib.SMTP(
                smtp_details["server"], smtp_details["port"], timeout=timeout
            ) as server:
                server.login(smtp_details["username"], smtp_details["password"])
                server.sendmail(smtp_details["username"], recipients, msg.as_string())

        return {"status": "success", "message": "Email sending successful!"}

    except smtplib.SMTPAuthenticationError:
        return {
            "status": "error",
            "message": "Authentication failed. Check your username and password.",
        }
    except smtplib.SMTPConnectError:
        return {
            "status": "error",
            "message": "Connection failed. Check the SMTP server and port.",
        }
    except socket.timeout:
        return {
            "status": "error",
            "message": "Connection timed out. The server may not be reachable.",
        }
    except Exception as e:
        import traceback

        traceback.print_exc()
        return {"status": "error", "message": str(e)}


async def async_send_email(smtp_details, email_subject, email_body, recipients, cc=None):
    try:
        msg = MIMEMultipart()
        msg["From"] = smtp_details["username"]
        msg["To"] = ", ".join(recipients)
        msg["Subject"] = email_subject

        if cc:
            msg["Cc"] = ", ".join(cc)
            recipients += cc

        msg.attach(MIMEText(email_body, "html"))

        # Determine SSL or plain SMTP based on the port
        if smtp_details["port"] == 465:
            # For SSL (typically port 465)
            response = await aiosmtplib.send(
                msg,
                hostname=smtp_details["server"],
                port=smtp_details["port"],
                username=smtp_details["username"],
                password=smtp_details["password"],
                use_tls=True,
                timeout=5,
            )
        else:
            # For plain SMTP or STARTTLS (typically port 587 or others)
            response = await aiosmtplib.send(
                msg,
                hostname=smtp_details["server"],
                port=smtp_details["port"],
                username=smtp_details["username"],
                password=smtp_details["password"],
                start_tls=True if smtp_details["port"] == 587 else False,
                timeout=5,
            )

        if 'OK' in response[1] or response[0] == "250":
            return {"status": "success", "message": "Email sent successfully!"}
        else:
            return {"status": "error", "message": "Failed to send email."}

    except aiosmtplib.SMTPAuthenticationError:
        return {
            "status": "error",
            "message": "Authentication failed. Check your username and password.",
        }
    except aiosmtplib.SMTPConnectError:
        return {
            "status": "error",
            "message": "Connection failed. Check the SMTP server and port.",
        }
    except asyncio.TimeoutError:
        return {
            "status": "error",
            "message": "Connection timed out. The server may not be reachable.",
        }
    except Exception as e:
        import traceback
        traceback.print_exc()
        return {"status": "error", "message": str(e)}