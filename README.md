# Project Overview

This project is a notification management system built using Flask and PostgreSQL. It allows users to manage various types of notifications, including email and web notifications, with customizable settings, templates, and mediums.

## Features

- **Notification Settings**: Configure notifications based on types, enabled statuses, and associated mediums.
- **Email Management**: Integrate SMTP settings for sending emails with specified templates, ensuring secure and efficient email delivery.
- **Customizable Templates**: Create and manage email templates for different notification scenarios, allowing for tailored messaging.
- **Multiple Notification Mediums**: Support for various notification mediums, including email and web alerts, enabling flexible notification delivery.
- **Scheduling**: Set notifications to trigger a specified number of days before important events, with customizable color codes for visual cues.

## Endpoints

The project includes several RESTful API endpoints to interact with notification settings, email templates, SMTP configurations, and notification days. These endpoints allow for CRUD operations on all entities, ensuring comprehensive management of notifications.

## Getting Started

1. **Clone the repository**.
2. **Install poetry for dependency management**
3. **Install required packages** using `poetry install`.
4. **Run the Flask application** using `python app.py`.
