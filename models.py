import datetime
import json
from flask_sqlalchemy import SQLAlchemy
from app import fernet

db = SQLAlchemy()


class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "expiry": str(self.expiry),
        }


class SMTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(255), nullable=False)
    use_tls = db.Column(db.Boolean, default=True)

    def __init__(
        self, server: str, port: int, username: str, password: str, use_tls: bool = True
    ):
        self.server = server
        self.port = port
        self.username = username
        self.password = self.encrypt_password(password)
        self.use_tls = use_tls

    def encrypt_password(self, password: str) -> str:
        return fernet.encrypt(password.encode()).decode()

    def decrypt_password(self) -> str:
        return fernet.decrypt(self.password.encode()).decode()

    def to_dict(self):
        return {
            "id": self.id,
            "server": self.server,
            "port": self.port,
            "username": self.username,
            "password": self.decrypt_password(),
            "use_tls": self.use_tls,
        }


class NotificationType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class NotificationSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name}


class NotificationMediums(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_settings_id = db.Column(db.Integer, nullable=False)
    notification_type_id = db.Column(db.Integer, nullable=False)
    smtp_id = db.Column(db.Integer, nullable=True)
    enabled = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "notification_settings_id": self.notification_settings_id,
            "notification_type_id": self.notification_type_id,
            "smtp_id": self.smtp_id,
            "enabled": self.enabled,
        }


class NotificationDays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_medium_id = db.Column(db.Integer, nullable=False)
    start_day = db.Column(db.Integer, nullable=False)
    end_day = db.Column(db.Integer, nullable=False)
    color_code = db.Column(db.String(10), nullable=False)
    email_subject = db.Column(db.String(100), nullable=True)
    email_body = db.Column(db.Text, nullable=True)
    email_recipients = db.Column(db.Text, nullable=True)
    email_cc = db.Column(db.Text, nullable=True)

    def to_dict(self):
        return {
            "id": self.id,
            "notification_medium_id": self.notification_medium_id,
            "start_day": self.start_day,
            "end_day": self.end_day,
            "color_code": self.color_code,
            "email_subject": self.email_subject,
            "email_body": self.email_body,
            "email_recipients": (
                json.loads(self.email_recipients) if self.email_recipients else []
            ),
            "email_cc": json.loads(self.email_cc) if self.email_cc else [],
        }


class WebNotificationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    heading = db.Column(db.String(128), nullable=True)
    body = db.Column(db.String(255), nullable=True)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())

    def to_dict(self):
        return {
            "id": self.id,
            "heading": self.heading,
            "body": self.body,
            "is_read": self.is_read,
            "created_at": self.created_at,
        }

class EmailNotificationItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    smtp_id = db.Column(db.Integer, nullable=True)
    email_subject = db.Column(db.String(100), nullable=True)
    email_body = db.Column(db.Text, nullable=True)
    email_recipients = db.Column(db.Text, nullable=True)
    email_cc = db.Column(db.Text, nullable=True)
    is_sent = db.Column(db.Boolean, default=False, index=True)
    retry_count = db.Column(db.Integer, default=0)
    last_error_message = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.datetime.now())
    executed_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "smtp_id": self.smtp_id,
            "email_subject": self.email_subject,
            "email_body": self.email_body,
            "email_recipients": (
                json.loads(self.email_recipients) if self.email_recipients else []
            ),
            "email_cc": json.loads(self.email_cc) if self.email_cc else [],
            "is_sent": self.is_sent,
            "created_at": self.created_at,
            "executed_at": self.executed_at,
        }
