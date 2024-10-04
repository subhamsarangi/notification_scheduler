from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


class PurchaseOrder(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    expiry = db.Column(db.Date, nullable=False)


class SMTP(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    server = db.Column(db.String(100), nullable=False)
    port = db.Column(db.Integer, nullable=False)
    username = db.Column(db.String(100), nullable=False)
    password = db.Column(db.String(100), nullable=False)
    use_tls = db.Column(db.Boolean, default=True)


class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    cc = db.Column(db.String(100))


class NotificationType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class NotificationSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


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


class NotificationDays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_medium_id = db.Column(
        db.Integer, db.ForeignKey("notification_mediums.id"), nullable=False
    )
    days_before = db.Column(db.Integer, nullable=False)
    color_code = db.Column(db.String(10), nullable=False)
