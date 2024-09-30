from flask import Flask, jsonify, render_template
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import text
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


# Create the database and tables
with app.app_context():
    db.create_all()


@app.route("/debug", methods=["GET"])
def debug_view():
    return "<h1>Debug Toolbar Test</h1>"


# Define the route to get PurchaseOrders with color codes
@app.route("/purchase_orders", methods=["GET"])
def get_purchase_orders():
    current_date = datetime.now().date()

    # Raw SQL query to get purchase orders
    purchase_orders_query = "SELECT id, name, expiry FROM purchase_order"
    purchase_orders = db.session.execute(text(purchase_orders_query)).fetchall()
    print(purchase_orders)

    response = []

    # Raw SQL query to get notification days
    notification_days_query = """
        SELECT nd.days_before, nd.color_code
        FROM notification_days nd
        JOIN notification_settings ns ON nd.notification_settings_id = ns.id
        WHERE ns.name = 'PO Expiry Notification'
        ORDER BY nd.days_before
    """
    notification_days = db.session.execute(text(notification_days_query)).fetchall()
    print(notification_days, "-------------------------------")
    for po in purchase_orders:
        future_date = datetime.strptime(str(po[2]), "%Y-%m-%d").date()
        difference = (future_date - current_date).days
        color_code = None

        for x in notification_days:
            if difference <= x[0]:
                color_code = x[1]
                break

        response.append(
            {
                "id": po[0],
                "name": po[1],
                "expiry": str(po[2]),
                "color_code": color_code,
            }
        )

    return render_template("index.html", response=response)
    return jsonify(response)


if __name__ == "__main__":
    app.run(debug=True, port=5001)
