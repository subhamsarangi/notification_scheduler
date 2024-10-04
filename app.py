from flask import Flask, jsonify, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_debugtoolbar import DebugToolbarExtension

app = Flask(__name__)
app.debug = True
app.config["SECRET_KEY"] = "opensecret"

app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///notifications.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
app.config["SQLALCHEMY_RECORD_QUERIES"] = True

db = SQLAlchemy(app)

toolbar = DebugToolbarExtension(app)
app.config["DEBUG_TB_PROFILER_ENABLED"] = True


# Define your models
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


# Create the database and tables
with app.app_context():
    db.create_all()


@app.route("/purchase_orders", methods=["GET"])
def get_purchase_orders():
    current_date = datetime.now().date()
    purchase_orders = PurchaseOrder.query.all()
    response = []

    notification_name = "PO Expiry"

    # Build the query for NotificationDays with search filters
    query = NotificationDays.query.join(NotificationMediums).join(NotificationSettings)

    # Apply filters based on search parameters
    if notification_name:
        query = query.filter(NotificationSettings.name.ilike(f"%{notification_name}%"))
    query = query.filter(NotificationMediums.enabled == True)

    notification_days = query.order_by(NotificationDays.days_before).all()

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

    return render_template("index.html", response=response)


if __name__ == "__main__":
    app.run(debug=True)
