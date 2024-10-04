from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.Date, nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "expiry": str(self.expiry),  # Convert date to string
        }


class SMTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    use_tls = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "server": self.server,
            "port": self.port,
            "username": self.username,
            "use_tls": self.use_tls,
        }


class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    cc = db.Column(db.String(100))

    def to_dict(self):
        return {
            "id": self.id,
            "subject": self.subject,
            "body": self.body,
            "sender": self.sender,
            "cc": self.cc,
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
    notification_settings_id = db.Column(
        db.Integer, db.ForeignKey("notification_settings.id"), nullable=False
    )
    notification_type_id = db.Column(
        db.Integer, db.ForeignKey("notification_type.id"), nullable=False
    )
    email_template_id = db.Column(
        db.Integer, db.ForeignKey("email_template.id"), nullable=True
    )
    smtp_id = db.Column(db.Integer, db.ForeignKey("smtp.id"), nullable=True)
    enabled = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "notification_settings_id": self.notification_settings_id,
            "notification_type_id": self.notification_type_id,
            "email_template_id": self.email_template_id,
            "smtp_id": self.smtp_id,
            "enabled": self.enabled,
        }


class NotificationDays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_medium_id = db.Column(
        db.Integer, db.ForeignKey("notification_mediums.id"), nullable=False
    )
    days_before = db.Column(db.Integer, nullable=False)
    color_code = db.Column(db.String(10), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "notification_medium_id": self.notification_medium_id,
            "days_before": self.days_before,
            "color_code": self.color_code,
        }
