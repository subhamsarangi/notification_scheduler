from flask import Flask, jsonify, render_template
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


class NotificationType(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)


class EmailTemplate(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    subject = db.Column(db.String(100), nullable=False)
    body = db.Column(db.Text, nullable=False)
    sender = db.Column(db.String(100), nullable=False)
    cc = db.Column(db.String(100))


class NotificationSettings(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    notification_type_id = db.Column(
        db.Integer, db.ForeignKey("notification_type.id"), nullable=False
    )
    enabled = db.Column(db.Boolean, default=True)
    smtp_id = db.Column(db.Integer, db.ForeignKey("smtp.id"), nullable=False)
    email_template_id = db.Column(
        db.Integer, db.ForeignKey("email_template.id"), nullable=False
    )


class NotificationDays(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    notification_settings_id = db.Column(
        db.Integer, db.ForeignKey("notification_settings.id"), nullable=False
    )
    days_before = db.Column(db.Integer, nullable=False)
    color_code = db.Column(db.String(10), nullable=False)


# Create the database and tables
with app.app_context():
    db.create_all()


# Define the route to get PurchaseOrders with color codes
@app.route("/purchase_orders", methods=["GET"])
def get_purchase_orders():
    current_date = datetime.now().date()
    purchase_orders = PurchaseOrder.query.all()
    response = []

    notification_days = (
        NotificationDays.query.join(NotificationSettings)
        .filter(
            NotificationSettings.name == "PO Expiry Notification",
        )
        .order_by(NotificationDays.days_before)
        .all()
    )
    print(notification_days)
    for po in purchase_orders:
        future_date = datetime.strptime(str(po.expiry), "%Y-%m-%d").date()
        difference = (future_date - current_date).days
        print(po.id, difference)
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

    # return jsonify(response)
    return render_template("index.html", response=response)


if __name__ == "__main__":
    app.run(debug=True)
