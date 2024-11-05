import os
from datetime import datetime, timedelta
import json

from flask import (
    Blueprint,
    request,
    jsonify,
    make_response,
    send_file,
    after_this_request,
    render_template,
)
from flask.views import MethodView
from flask_cors import cross_origin

from utils import handle_exceptions, check_smtp, send_email, smtp_details
from models import (
    db,
    PurchaseOrder,
    SMTP,
    NotificationType,
    NotificationSettings,
    NotificationMediums,
    NotificationDays,
    WebNotificationItem,
)


api = Blueprint("api", __name__)


# DOWNLAD FILE TESTING
@api.route("/download/<filename>", methods=["GET"])
def download_file(filename):
    try:
        current_dir = os.getcwd()
        file_path = os.path.join(current_dir, "files", filename)

        if os.path.exists(file_path):

            @after_this_request
            def remove_file(response):
                try:
                    os.remove(file_path)
                    print(f"File {filename} deleted successfully.")
                except Exception as e:
                    print(f"Error deleting file {filename}: {e}")
                return response

            return send_file(file_path, as_attachment=True)
        else:
            return jsonify({"error": "File not found"}), 404
    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": "An error occurred"}), 500


# EMAIL TESTING
@api.route("/send-email", methods=["GET"])
def send_email_view():
    try:
        email_data = {
            "email_body": f"Hey <b>{{username}}</b> how was the {{product_name}}",
            "email_cc": ["subhamsarangi2016@gmail.com"],
            "email_recipients": ["subham.ivanweb@gmail.com", "ivan.sarangi@gmail.com"],
            "email_subject": "TEST Recently Purchased Dummy order",
        }

        context = {"username": "Subham", "product_name": "Product XYZ"}

        EMAIL_CONTENT = email_data["email_body"].format(**context)
        email_body = render_template("email.html", content=EMAIL_CONTENT)

        email_send_result = send_email(
            smtp_details,
            email_data["email_subject"],
            email_body,
            email_data["email_recipients"],
            email_data["email_cc"],
        )

        if email_send_result["status"] == "success":
            return jsonify(email_send_result), 200
        else:
            return jsonify(email_send_result), 500

    except Exception as e:
        import traceback

        traceback.print_exc()
        return jsonify({"error": f"An unexpected error occurred. {str(e)}"}), 500


# LISTING
class PurchaseOrderView(MethodView):
    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def get(self):
        purchase_orders = PurchaseOrder.query.all()
        notification_name = "PO Expiry"
        notification_days = (
            NotificationDays.query.select_from(NotificationDays)
            .join(
                NotificationMediums,
                NotificationDays.notification_medium_id == NotificationMediums.id,
            )
            .join(
                NotificationSettings,
                NotificationMediums.notification_settings_id == NotificationSettings.id,
            )
            .filter(NotificationSettings.name.ilike(f"%{notification_name}%"))
            .filter(NotificationMediums.enabled == True)
            .order_by(NotificationDays.start_day)
            .all()
        )
        data = []
        for po in purchase_orders:
            po = po.to_dict()
            future_date = datetime.strptime(str(po["expiry"]), "%Y-%m-%d").date()
            current_date = datetime.now().date()
            difference = (future_date - current_date).days
            color_code = None
            for x in notification_days:
                if x.start_day <= difference <= x.end_day:
                    color_code = x.color_code
                    break

            po["color_code"] = color_code
            data.append(po)

        response = {
            "status": "success",
            "message": "PO Master fetched successfully",
            "POMasterList": data,
        }
        return make_response(jsonify(response)), 200


# SCHEDULED JOB
class ProcessPoExpirations(MethodView):
    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def get(self):
        notification_name = "PO Expiry"
        notification_days = (
            db.session.query(NotificationDays, NotificationMediums.smtp_id)
            .select_from(NotificationDays)
            .join(
                NotificationMediums,
                NotificationDays.notification_medium_id == NotificationMediums.id,
            )
            .join(
                NotificationSettings,
                NotificationMediums.notification_settings_id == NotificationSettings.id,
            )
            .filter(NotificationSettings.name.ilike(f"%{notification_name}%"))
            .filter(NotificationMediums.enabled == True)
            .order_by(NotificationDays.start_day)
            .all()
        )
        start_day_values = [x.start_day for x, _ in notification_days] or [0]
        least_day = min(start_day_values)
        least_date = (datetime.now() + timedelta(days=least_day)).strftime("%Y-%m-%d")

        end_day_values = [x.end_day for x, _ in notification_days] or [0]
        highest_day = max(end_day_values)
        highest_date = (datetime.now() + timedelta(days=highest_day)).strftime(
            "%Y-%m-%d"
        )

        purchase_orders = (
            db.session.query(PurchaseOrder)
            .filter(PurchaseOrder.expiry.between(least_date, highest_date))
            .all()
        )
        data = []
        for po in purchase_orders:
            po = po.to_dict()
            context = {
                "expiry_date": po["expiry"],
                "po_number": po["name"],
            }
            data.append(po)
            future_date = datetime.strptime(str(po["expiry"]), "%Y-%m-%d").date()
            current_date = datetime.now().date()
            difference = (future_date - current_date).days
            context["difference"] = difference

            notification_heading = "PO expiry alert"

            for x, smtp_id in notification_days:
                if difference < 0:
                    if difference >= x.start_day:
                        notification_body = "PO {po_number} has expired {difference} day(s) ago on {expiry_date}"
                    else:
                        continue
                elif difference > 0:
                    if difference <= x.end_day:
                        notification_body = "PO {po_number} will expire in {difference} day(s) on {expiry_date}"
                    else:
                        continue
                else:
                    if difference == x.start_day and difference == x.end_day:
                        notification_body = "PO {po_number} has expired today"
                    else:
                        continue

                NOTIFICATION_CONTENT = notification_body.format(**context)
                existing_notification = (
                    db.session.query(WebNotificationItem)
                    .filter_by(body=NOTIFICATION_CONTENT)
                    .first()
                )
                if existing_notification:
                    break
                else:
                    new_web_notification = WebNotificationItem(
                        **{
                            "heading": notification_heading,
                            "body": NOTIFICATION_CONTENT,
                        }
                    )
                    db.session.add(new_web_notification)
                    print(f'{po["name"]} Notification created.')

                    # send mail
                    smtp_details = None
                    if smtp_id is not None:
                        smtp_details = SMTP.query.get(smtp_id)
                    else:
                        notification_medium = NotificationMediums.query.get(
                            x.notification_medium_id
                        )
                        if notification_medium and notification_medium.smtp_id:
                            smtp_details = SMTP.query.get(notification_medium.smtp_id)
                    if smtp_details:
                        smtp_details = smtp_details.to_dict()
                    else:
                        print(f'{po["name"]} Mail not sent.')
                        continue

                    EMAIL_CONTENT = x.email_body.format(**context)
                    email_body = render_template("email.html", content=EMAIL_CONTENT)
                    email_send_result = send_email(
                        smtp_details,
                        x.email_subject,
                        email_body,
                        eval(x.email_recipients),
                        eval(x.email_cc),
                    )
                    print(email_send_result["message"])
                break
        db.session.commit()
        response = {
            "status": "success",
            "message": "Expiring PO Processed successfully",
            "data": data,
        }
        return make_response(jsonify(response)), 200


# SMTP
class SMTPSettingsView(MethodView):
    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def get(self):
        smtp_settings = SMTP.query.all()
        return jsonify(
            {
                "message": "SMTP setting list fetched",
                "status": "success",
                "data": [s.to_dict() for s in smtp_settings],
            }
        )

    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def post(self):
        data = request.json
        new_smtp = SMTP(**data)
        smtp_check_result = check_smtp(new_smtp.to_dict())
        if smtp_check_result["status"] == "error":
            return jsonify(smtp_check_result)
        db.session.add(new_smtp)
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "SMTP Setting validated and created",
                    "status": "success",
                    "data": new_smtp.to_dict(),
                }
            ),
            201,
        )


class SMTPSettingsByIdView(MethodView):
    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def get(self, id):
        smtp = SMTP.query.get_or_404(id)
        return jsonify(
            {
                "message": "SMTP Setting fetched",
                "status": "success",
                "data": smtp.to_dict(),
            }
        )

    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def post(self, id):
        smtp = SMTP.query.get_or_404(id)
        data = request.json
        smtp_check_result = check_smtp(data)
        if smtp_check_result["status"] == "error":
            return jsonify(smtp_check_result)
        for key, value in data.items():
            if "password" in key:
                setattr(smtp, key, smtp.encrypt_password(value))
            else:
                setattr(smtp, key, value)
        db.session.flush()
        db.session.commit()
        return jsonify(
            {
                "message": "SMTP Setting validated and updated",
                "status": "success",
                "data": smtp.to_dict(),
            }
        )


# NOTIFICATION SETTINGS
class NotificationSettingsView(MethodView):
    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def get(self):
        notification_settings = NotificationSettings.query.all()
        data = [ns.to_dict() for ns in notification_settings]
        for item in data:
            notification_mediums = (
                db.session.query(NotificationMediums, NotificationType.name)
                .select_from(NotificationMediums)
                .join(
                    NotificationType,
                    NotificationMediums.notification_type_id == NotificationType.id,
                )
                .filter(NotificationMediums.notification_settings_id == item["id"])
                .all()
            )

            mediums = []
            for medium, notification_type_name in notification_mediums:
                mediums.append(
                    {
                        "id": medium.id,
                        "enabled": medium.enabled,
                        "notification_type_name": notification_type_name,
                        "smtp_id": medium.smtp_id,
                    }
                )
            item["mediums"] = mediums

        return jsonify(
            {
                "message": "Notification Settings list fetched",
                "status": "success",
                "data": data,
            }
        )

    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def post(self):  # WONT BE USED BY USER BUT BY ADMIN
        data = request.json
        new_setting = NotificationSettings(**data)
        db.session.add(new_setting)

        notification_types = NotificationType.query.all()

        smtp_id = None
        smtp_settings = SMTP.query.all()
        if smtp_settings:
            smtp_id = smtp_settings[0].to_dict()["id"]

        for notification_type in notification_types:
            new_medium = NotificationMediums(
                notification_settings_id=new_setting.id,
                notification_type_id=notification_type.id,
                enabled=False,
                smtp_id=smtp_id,
            )
            db.session.add(new_medium)

        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Notification Settings created",
                    "status": "success",
                    "data": new_setting.to_dict(),
                }
            ),
            201,
        )


class NotificationSettingsByIdView(MethodView):
    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def get(self, id):  # WONT BE USED BY USER
        notification_setting = NotificationSettings.query.get_or_404(id)
        return jsonify(
            {
                "message": "Notification Settings fetched",
                "status": "success",
                "data": notification_setting.to_dict(),
            }
        )

    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def post(self, id):  # WONT BE USED BY USER
        notification_setting = NotificationSettings.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            setattr(notification_setting, key, value)
        db.session.commit()
        return jsonify(
            {
                "message": "Notification Settings list updated",
                "status": "success",
                "data": notification_setting.to_dict(),
            }
        )


# NOTIFICATION MEDIUMS
class NotificationMediumByIdView(MethodView):
    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def get(self, id):
        medium = NotificationMediums.query.get_or_404(id)
        return jsonify(
            {
                "message": "Notification medium fetched",
                "status": "success",
                "data": medium.to_dict(),
            }
        )

    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def post(self, id):
        medium = NotificationMediums.query.get_or_404(id)
        data = request.json
        for key, value in data.items():
            setattr(medium, key, value)
        db.session.commit()
        return jsonify(
            {
                "message": "Notification medium updated",
                "status": "success",
                "data": medium.to_dict(),
            }
        )


# NOTIFICATION DAYS
class NotificationDaysView(MethodView):
    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def get(self):
        notification_medium_id = request.args.get("notification_medium_id")
        days = NotificationDays.query.filter(
            NotificationDays.notification_medium_id == notification_medium_id
        ).all()
        if days:
            return jsonify(
                {
                    "message": "Notification days list fetched based on the medium id",
                    "status": "success",
                    "data": [nd.to_dict() for nd in days],
                }
            )
        else:
            return jsonify(
                {
                    "message": "Notification days not found for the medium id",
                    "status": "error",
                }
            )

    @cross_origin(supports_credentials=True)
    @handle_exceptions
    def post(self):
        data = request.get_json()
        if not isinstance(data, list):
            return (
                jsonify(
                    {
                        "message": "Invalid data format, expected a list.",
                        "status": "error",
                    }
                ),
                400,
            )

        updated_or_created = []

        for item in data:
            notification_day = None

            if "id" in item:
                notification_day = NotificationDays.query.get(item["id"])

            if notification_day:  # existing record
                for key, value in item.items():
                    if key != "id":
                        if key in ["email_cc", "email_recipients"] and isinstance(
                            value, list
                        ):
                            setattr(notification_day, key, json.dumps(value))
                        else:
                            setattr(notification_day, key, value)
            else:  # new record
                if "email_cc" in item and isinstance(item["email_cc"], list):
                    item["email_cc"] = json.dumps(item["email_cc"])

                if "email_recipients" in item and isinstance(
                    item["email_recipients"], list
                ):
                    item["email_recipients"] = json.dumps(item["email_recipients"])

                notification_day = NotificationDays(**item)
                db.session.add(notification_day)

            updated_or_created.append(notification_day)
        db.session.flush()
        db.session.commit()
        return (
            jsonify(
                {
                    "message": "Notification days have been created/updated successfully.",
                    "status": "success",
                    "data": [nd.to_dict() for nd in updated_or_created],
                }
            ),
            201,
        )


# URL RULES
api.add_url_rule(
    "/purchase_orders",
    view_func=PurchaseOrderView.as_view("purchase_orders"),
    methods=["GET"],
)
api.add_url_rule(
    "/process_po_expirations",
    view_func=ProcessPoExpirations.as_view("process_po_expirations"),
    methods=["GET"],
)
# 0 3 * * * curl -s http://localhost:5000/process_po_expirations

api.add_url_rule(
    "/smtp",
    view_func=SMTPSettingsView.as_view("smtp_settings"),
    methods=["GET", "POST"],
)
api.add_url_rule(
    "/smtp/<int:id>",
    view_func=SMTPSettingsByIdView.as_view("smtp_settings_by_id"),
    methods=["GET", "DELETE", "POST"],
)

api.add_url_rule(
    "/notification-settings",
    view_func=NotificationSettingsView.as_view("notification_settings"),
    methods=["GET", "POST"],
)
api.add_url_rule(
    "/notification-settings/<int:id>",
    view_func=NotificationSettingsByIdView.as_view("notification_settings_by_id"),
    methods=["GET", "POST"],
)


api.add_url_rule(
    "/notification-mediums/<int:id>",
    view_func=NotificationMediumByIdView.as_view("notification_medium_by_id"),
    methods=["GET", "POST"],
)

api.add_url_rule(
    "/notification-days",
    view_func=NotificationDaysView.as_view("notification_days"),
    methods=["GET", "POST"],
)
