

| Activity                                      | URL                                   | Method | Payload Structure                                            | Query Params             | Path Params |
| --------------------------------------------- | ------------------------------------- | ------ | ------------------------------------------------------------ | ------------------------ | ----------- |
| List of filtered and paginated PurchaseOrders | `/api/purchaseorders`                 | GET    | -                                                            | `page`, `size`, `filter` | -           |
| List of SMTP settings                         | `/api/smtp`                           | GET    | -                                                            | -                        | -           |
| Create SMTP setting                           | `/api/smtp`                           | POST   | `{ "server": "string", "port": "number", "username": "string", "password": "string", "use_tls": "boolean" }` | -                        | -           |
| SMTP setting details                          | `/api/smtp/{id}`                      | GET    | -                                                            | -                        | `id`        |
| Update SMTP setting                           | `/api/smtp/{id}`                      | POST   | `{ "server": "string", "port": "number", "username": "string", "password": "string", "use_tls": "boolean" }` | -                        | `id`        |
| List of Notification Types                    | `/api/notification-types`             | GET    | -                                                            | -                        | -           |
| Create Notification Type                      | `/api/notification-types`             | POST   | `{ "name": "string" }`                                       | -                        | -           |
| Notification Type details                     | `/api/notification-types/{id}`        | GET    | -                                                            | -                        | `id`        |
| Update Notification Type                      | `/api/notification-types/{id}`        | POST   | `{ "name": "string" }`                                       | -                        | `id`        |
| List of Notification Settings                 | `/api/notification-settings`          | GET    | -                                                            | -                        | -           |
| Create Notification Setting                   | `/api/notification-settings`          | POST   | `{ "name": "string" }`                                       | -                        | -           |
| Notification Setting details                  | `/api/notification-settings/{id}`     | GET    | -                                                            | -                        | `id`        |
| Update Notification Setting                   | `/api/notification-settings/{id}`     | POST   | `{ "name": "string" }`                                       | -                        | `id`        |
| Update Notification Medium                    | `/api/notification-mediums/{id}`      | POST   | `{ "enabled": "boolean" }`                                   | -                        | `id`        |
| List of Notification Days                     | `/api/notification-days`              | GET    | -                                                            | -                        | -           |
| Create Notification Day                       | `/api/notification-days`              | POST   | `{ "notification_medium_id": "number", "days_before": "number", "color_code": "string" }` | -                        | -           |
| Notification Day details                      | `/api/notification-days/{id}`         | GET    | -                                                            | -                        | `id`        |
| Update Notification Day                       | `/api/notification-days/{id}`         | POST   | `{ "days_before": "number", "color_code": "string" }`        | -                        | `id`        |
| List of Notification Days for Medium          | `/api/notification-mediums/{id}/days` | GET    | -                                                            | -                        | `id`        |

