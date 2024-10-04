from flask import Blueprint, request, jsonify, render_template
from datetime import datetime


from utils import handle_exceptions
from models import (
    db,
    PurchaseOrder,
    SMTP,
    NotificationType,
    EmailTemplate,
    NotificationSettings,
    NotificationMediums,
    NotificationDays,
)

api = Blueprint("api", __name__)


# list purchase orders
@api.route("/purchase_orders", methods=["GET"])
@handle_exceptions
def get_purchase_orders():
    current_date = datetime.now().date()
    purchase_orders = PurchaseOrder.query.all()
    response = []

    notification_name = "PO Expiry"

    notification_days = (
        NotificationDays.query.join(NotificationMediums)
        .join(NotificationSettings)
        .filter(NotificationSettings.name.ilike(f"%{notification_name}%"))
        .filter(NotificationMediums.enabled == True)
        .order_by(NotificationDays.days_before)
        .all()
    )

    for po in purchase_orders:
        future_date = datetime.strptime(str(po.expiry), "%Y-%m-%d").date()
        difference = (future_date - current_date).days
        color_code = None

        for x in notification_days:
            if difference <= x.days_before:
                color_code = x.color_code
                break

        response.append(
            {
                "id": po.id,
                "name": po.name,
                "expiry": str(po.expiry),
                "color_code": color_code,
            }
        )

    return jsonify(response)
    return render_template("index.html", response=response)


# list and create smtp settings
@api.route("/smtp", methods=["GET", "POST"])
@handle_exceptions
def handle_smtp():
    if request.method == "GET":
        smtp_settings = SMTP.query.all()
        return jsonify([s.to_dict() for s in smtp_settings])

    if request.method == "POST":
        data = request.json
        new_smtp = SMTP(**data)
        db.session.add(new_smtp)
        db.session.commit()
        return jsonify(new_smtp.to_dict()), 201


# view and update a smtp setting
@api.route("/smtp/<int:id>", methods=["GET", "POST"])
@handle_exceptions
def handle_smtp_by_id(id):
    smtp = SMTP.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(smtp.to_dict())

    if request.method == "POST":
        data = request.json
        for key, value in data.items():
            setattr(smtp, key, value)
        db.session.commit()
        return jsonify(smtp.to_dict())


# list and create notification types
@api.route("/notification-types", methods=["GET", "POST"])
@handle_exceptions
def handle_notification_types():
    if request.method == "GET":
        notification_types = NotificationType.query.all()
        return jsonify([nt.to_dict() for nt in notification_types])

    if request.method == "POST":
        data = request.json
        new_type = NotificationType(**data)
        db.session.add(new_type)
        db.session.commit()
        return jsonify(new_type.to_dict()), 201


# view and update notification types
@api.route("/notification-types/<int:id>", methods=["GET", "POST"])
@handle_exceptions
def handle_notification_type_by_id(id):
    notification_type = NotificationType.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(notification_type.to_dict())

    if request.method == "POST":
        data = request.json
        for key, value in data.items():
            setattr(notification_type, key, value)
        db.session.commit()
        return jsonify(notification_type.to_dict())


# list and create email templates
@api.route("/email-templates", methods=["GET", "POST"])
@handle_exceptions
def handle_email_templates():
    if request.method == "GET":
        email_templates = EmailTemplate.query.all()
        return jsonify([et.to_dict() for et in email_templates])

    if request.method == "POST":
        data = request.json
        new_template = EmailTemplate(**data)
        db.session.add(new_template)
        db.session.commit()
        return jsonify(new_template.to_dict()), 201


# view and update an email template
@api.route("/email-templates/<int:id>", methods=["GET", "POST"])
@handle_exceptions
def handle_email_template_by_id(id):
    email_template = EmailTemplate.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(email_template.to_dict())

    if request.method == "POST":
        data = request.json
        for key, value in data.items():
            setattr(email_template, key, value)
        db.session.commit()
        return jsonify(email_template.to_dict())


# List and create Notification Settings
@api.route("/notification-settings", methods=["GET", "POST"])
@handle_exceptions
def handle_notification_settings():
    if request.method == "GET":
        notification_settings = NotificationSettings.query.all()
        return jsonify([ns.to_dict() for ns in notification_settings])

    if request.method == "POST":
        data = request.json
        new_setting = NotificationSettings(**data)
        db.session.add(new_setting)
        db.session.commit()

        # Retrieve all NotificationType instances
        notification_types = NotificationType.query.all()

        # Create corresponding NotificationMedium objects
        for notification_type in notification_types:
            new_medium = NotificationMediums(
                notification_settings_id=new_setting.id,
                notification_type_id=notification_type.id,
                enabled=True,
            )
            db.session.add(new_medium)

        db.session.commit()
        return jsonify(new_setting.to_dict()), 201


# view and update a notification settings
@api.route("/notification-settings/<int:id>", methods=["GET", "POST"])
@handle_exceptions
def handle_notification_setting_by_id(id):
    notification_setting = NotificationSettings.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(notification_setting.to_dict())

    if request.method == "POST":
        data = request.json
        for key, value in data.items():
            setattr(notification_setting, key, value)
        db.session.commit()
        return jsonify(notification_setting.to_dict())


# List the notification Mediums
@api.route("/notification-mediums", methods=["GET"])
@handle_exceptions
def handle_notification_mediums():
    notification_settings_id = request.args.get("notification_settings_id")
    mediums = (
        db.session.query(NotificationMediums, NotificationType.name)
        .join(NotificationType)
        .filter(
            NotificationMediums.notification_settings_id == notification_settings_id
        )
        .all()
    )

    response = []
    for medium, notification_type_name in mediums:
        response.append(
            {
                "id": medium.id,
                "notification_settings_id": medium.notification_settings_id,
                "notification_type_id": medium.notification_type_id,
                "email_template_id": medium.email_template_id,
                "smtp_id": medium.smtp_id,
                "enabled": medium.enabled,
                "notification_type_name": notification_type_name,  # Accessing name directly from the query
            }
        )

    return jsonify(response)


# View and Update a notification Medium
@api.route("/notification-mediums/<int:id>", methods=["GET", "POST"])
@handle_exceptions
def handle_notification_medium_by_id(id):
    medium = NotificationMediums.query.get_or_404(id)
    if request.method == "GET":
        return jsonify(medium.to_dict())

    if request.method == "POST":
        data = request.json
        for key, value in data.items():
            setattr(medium, key, value)
        db.session.commit()
        return jsonify(medium.to_dict())


# list and create notification days
@api.route("/notification-days", methods=["GET", "POST"])
@handle_exceptions
def handle_notification_days():
    if request.method == "GET":
        days = NotificationDays.query.all()
        return jsonify([nd.to_dict() for nd in days])

    if request.method == "POST":
        data = request.json
        new_day = NotificationDays(**data)
        db.session.add(new_day)
        db.session.commit()
        return jsonify(new_day.to_dict()), 201


# update notification days
@api.route("/notification-days/<int:id>", methods=["POST"])
@handle_exceptions
def handle_notification_day_by_id(id):
    day = NotificationDays.query.get_or_404(id)
    if request.method == "POST":
        data = request.json
        for key, value in data.items():
            setattr(day, key, value)
        db.session.commit()
        return jsonify(day.to_dict())
