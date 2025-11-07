# SecureShop (Django)

A minimal e-commerce demo with security features for coursework.

## Quickstart

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
python manage.py makemigrations
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

## Features
- RBAC: staff-only product management
- CSRF, session-only cart (no PII in cookies)
- Password validators (min length 12)
- Secure cookie flags & basic security headers
- File upload validation (size/MIME)
- Audit logging of sign-in and orders
- Tiny POST rate limiter (demo)
