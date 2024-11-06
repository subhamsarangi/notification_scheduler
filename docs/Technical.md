# DB Schema

```
PurchaseOrder (id, name, expiry)

SMTP (id, server, port, username, password, use_tls)

NotificationType (id, name)

NotificationSettings (id, name)

NotificationMediums (id, notification_settings_id[FK], notification_type_id[FK], smtp_id[FK], enabled)

NotificationDays (id, notification_medium_id[FK], start_day, end_day, color_code, email_subject, email_body, email_recipients, email_cc)

WebNotificationItem (id, heading, body, is_read, created_at)

EmailNotificationItem (id, smtp_id, email_subject, email_body, email_recipients, email_cc, is_sent, retry_count, last_error_message, created_at, executed_at)
```
