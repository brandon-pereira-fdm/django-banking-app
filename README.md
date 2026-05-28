# BankApp MVP

BankApp is a local learning MVP for a server-rendered personal and business
banking web application. It follows the project constitution and the
Specification-Driven Development artifacts in `specs/001-banking-mvp/`.

## Scope

- Python, Django, SQLite3, Django templates, custom CSS, and Waitress only.
- SGD-only monetary operations.
- Personal Account transfers by unique phone number.
- Business Account transfers by unique company UEN.
- Business outgoing withdrawals and transfers require approval.

This project is not real banking software, does not move real money, and is not
suitable for public production deployment.

## Local Setup

Use the feature quickstart:

```text
specs/001-banking-mvp/quickstart.md
```

Typical commands:

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export DJANGO_SECRET_KEY='replace-with-local-development-secret'
export DJANGO_DEBUG='1'
export DJANGO_ALLOWED_HOSTS='127.0.0.1,localhost'
python manage.py migrate
python manage.py test
python manage.py runserver
```

Waitress local launch:

```bash
python -m waitress --listen=127.0.0.1:8000 bankapp.wsgi:application
```
