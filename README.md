# admin-email-automation-system
A Flask-based secure email management system with admin panel, OTP, face authentication, biometric/WebAuthn login, email scheduling, and multi-module access control.

# Secure Email Management System

A professional Flask-based secure email management system designed for administrative email operations with advanced authentication features. The project includes admin login, OTP verification, biometric/WebAuthn-based authentication, email sending, email scheduling, and dashboard-based access control.

## Features

- Secure admin authentication
- OTP-based login verification
- Biometric / WebAuthn authentication
- Admin and sub-admin access flow
- Email sending functionality
- Scheduled email delivery
- Dashboard-based system management
- Modular Flask project structure
- MySQL database integration
- Static and template-based frontend rendering

## Project Objective

The main objective of this project is to provide a secure and scalable email management platform where authorized users can log in using multiple authentication methods and manage email operations efficiently.

## Tech Stack

### Backend
- Python
- Flask

### Frontend
- HTML
- CSS
- JavaScript

### Database
- MySQL

### Authentication & Security
- OTP Authentication
- Biometric Authentication
- WebAuthn / Passkey Authentication

### Other Components
- Email Scheduler
- Admin Panel
- Modular Route Handling

## Project Structure

```bash
EMAIL_SYSTEM/
│
├── __pycache__/
├── .vscode/
├── models/
├── routes/
│   ├── __init__.py
│   ├── admin.py
│   ├── auth.py
│   ├── biometric.py
│   ├── email.py
│   ├── otp.py
│   └── webauthn.py
│
├── scheduler/
├── services/
├── static/
├── templates/
├── utils/
├── app.py
├── requirements.txt
└── README.md
```

## Main Modules

### 1. Authentication Module
Handles secure login and user access management.

### 2. OTP Module
Provides one-time password verification for secure login flow.

### 3. Biometric / WebAuthn Module
Supports secure authentication through biometric or passkey-based verification.

### 4. Email Module
Handles email composition and sending operations.

### 5. Scheduler Module
Manages scheduled email sending tasks.

### 6. Admin Module
Provides admin-related dashboard functions and system control.

## Installation Steps

### 1. Clone the repository
```bash
git clone https://github.com/your-username/secure-email-management-system.git
cd secure-email-management-system
```

### 2. Create virtual environment
```bash
python -m venv venv
```

### 3. Activate virtual environment

#### On Windows
```bash
venv\Scripts\activate
```

#### On macOS/Linux
```bash
source venv/bin/activate
```

### 4. Install dependencies
```bash
pip install -r requirements.txt
```

### 5. Configure database
Update your MySQL database credentials inside the project configuration file.

Example:
- Database name
- Username
- Password
- Host
- Port

### 6. Run the Flask application
```bash
python app.py
```

### 7. Open in browser
```bash
http://127.0.0.1:5000
```

## Requirements

Create a `requirements.txt` file if not already available.

Example dependencies may include:

```txt
Flask
Flask-MySQLdb
PyMySQL
pyotp
fido2
gunicorn
```

## Environment Variables

For security, sensitive credentials should be stored using environment variables, such as:

- SECRET_KEY
- DB_HOST
- DB_USER
- DB_PASSWORD
- DB_NAME
- MAIL_USERNAME
- MAIL_PASSWORD

## Use Cases

- Secure internal email management
- Admin-controlled email operations
- Multi-step authentication system
- Scheduled email automation
- Organizational communication workflow

## Future Enhancements

- Role-based permission control
- Multiple sender email management
- Email logs and analytics
- Attachment support
- Rich text email editor
- Audit trail for admin actions
- Deployment support on cloud platforms

## Screenshots

Add project screenshots here for:
- Login page
- OTP verification page
- Admin dashboard
- Email send page
- Scheduler page

## Deployment

This project can be deployed using:
- Render
- Railway
- Heroku
- VPS
- Docker

## Author

**Debanshu Sekhar Bal**

## License

This project is for educational, demonstration, and development purposes. You can add a proper open-source license if needed.
