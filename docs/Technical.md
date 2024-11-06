# DB Schema

```
PurchaseOrder (id, name, expiry)

SMTP (id, server, port, username, password, use_tls)

NotificationType (id, name)

NotificationSettings (id, name)

NotificationMediums (id, notification_settings_id[FK], notification_type_id[FK], smtp_id[FK], enabled)

NotificationDays (id, notification_medium_id[FK], start_day, end_day, color_code, email_subject, email_body, email_recipients, email_cc)

WebNotificationItem (id, heading, body, is_read, created_at)
```

# Views
File Download: The download_file route checks if a file exists, serves it as a downloadable attachment, and removes the file afterward.

Email Sending: The send_email_view route sends an email with a test message, with dynamic content filled in from a template.

## Purchase Order Management:
PurchaseOrderView retrieves purchase orders, calculates expiration days, and assigns a color code based on notification settings.
ProcessPoExpirations schedules PO expiration processing, generating notifications based on expiration dates and sending alerts via email and web notifications.

## SMTP Settings:

SMTPSettingsView and SMTPSettingsByIdView manage SMTP settings, including listing, validating, creating, and updating SMTP configurations.

## Notification Settings:
NotificationSettingsView and NotificationSettingsByIdView allow management of notification settings, linking notification mediums (like email) to notification types and enabling/disabling them.

### Table summarizing the routes, methods, and purposes

| **Route**                        | **HTTP Method** | **Purpose**                                                                                               |
|----------------------------------|-----------------|-----------------------------------------------------------------------------------------------------------|
| `/download/<filename>`           | GET            | Allows users to download a file, with automatic deletion of the file after download.                      |
| `/send-email`                    | GET            | Sends a test email with a templated message to specified recipients.                                      |
| `/purchase-orders`               | GET            | Fetches a list of purchase orders with color-coded expiration statuses based on notification settings.    |
| `/process-po-expirations`        | GET            | Processes purchase orders for nearing expiration, sends notifications, and logs expired orders.           |
| `/smtp-settings`                 | GET            | Retrieves a list of all SMTP settings stored in the database.                                             |
| `/smtp-settings`                 | POST           | Validates and creates a new SMTP setting.                                                                 |
| `/smtp-settings/<id>`            | GET            | Fetches SMTP settings by a specific ID.                                                                   |
| `/smtp-settings/<id>`            | POST           | Updates an existing SMTP setting, validating connection details before saving.                            |
| `/notification-settings`         | GET            | Retrieves all notification settings and their associated notification mediums.                            |
| `/notification-settings`         | POST           | Creates new notification settings (typically for administrative use).                                     |
| `/notification-settings/<id>`    | GET            | Retrieves notification settings by a specific ID (typically for administrative use).                      |
| `/notification-settings/<id>`    | POST           | Updates notification settings by a specific ID (typically for administrative use).                        |
