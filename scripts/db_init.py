from app import (
    app,
    db,
    PurchaseOrder,
    SMTP,
    NotificationType,
    EmailTemplate,
    NotificationSettings,
    NotificationMediums,
    NotificationDays,
)
from datetime import datetime, timedelta


# Function to add dummy data
def add_dummy_data():
    # Create some PurchaseOrders
    po1 = PurchaseOrder(name="Order 1", expiry=datetime.now() + timedelta(days=10))
    po2 = PurchaseOrder(name="Order 2", expiry=datetime.now() + timedelta(days=5))
    po3 = PurchaseOrder(name="Order 3", expiry=datetime.now() + timedelta(days=2))

    # Create some SMTP settings
    smtp1 = SMTP(
        server="smtp.example.com",
        port=587,
        username="user@example.com",
        password="password",
        use_tls=True,
    )

    # Create some EmailTemplates
    et1 = EmailTemplate(
        subject="Expiry Alert",
        body="Your purchase order is about to expire.",
        sender="alert@example.com",
        cc="cc@example.com",
    )

    # Create some NotificationTypes
    nt1 = NotificationType(name="Email Alert")
    nt2 = NotificationType(name="Web Alert")

    # Create some NotificationSettings
    ns1 = NotificationSettings(
        name="PO Expiry Notification",
    )

    # Create some NotificationMediums
    nm1 = NotificationMediums(
        notification_settings_id=1,
        notification_type_id=2,
        enabled=True,
        smtp_id=None,
        email_template_id=None,
    )

    nm2 = NotificationMediums(
        notification_settings_id=1,
        notification_type_id=2,
        enabled=True,
        smtp_id=1,
        email_template_id=1,
    )

    # Create some NotificationDays
    nd1 = NotificationDays(notification_medium_id=1, days_before=7, color_code="green")
    nd2 = NotificationDays(notification_medium_id=1, days_before=3, color_code="yellow")
    nd3 = NotificationDays(notification_medium_id=1, days_before=1, color_code="red")

    # Add all objects to the session
    db.session.add_all(
        [po1, po2, po3, smtp1, nt1, nt2, et1, ns1, nm1, nm2, nd1, nd2, nd3]
    )

    # Commit the session to the database
    db.session.commit()


if __name__ == "__main__":
    with app.app_context():
        add_dummy_data()
    print("Dummy data added successfully.")
