# Chaintech Event Management System

This repository contains a Django + DRF implementation of an Event Management API used for the Chaintech assignment.

Quick start

1. Create and activate a virtual environment (Windows PowerShell):

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
```

2. Install dependencies:

```powershell
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
```

3. Apply migrations and create a superuser:

```powershell
python manage.py migrate
python manage.py createsuperuser
```

4. Run the dev server:

```powershell
python manage.py runserver
```

API endpoints

- Obtain JWT token: `POST /api/token/` (body: username, password)
- Refresh token: `POST /api/token/refresh/`
- Events: `/api/events/`
- RSVP (event-level): `/api/events/{id}/rsvp/` and `/api/events/{id}/rsvp/{user_id}/` (PATCH)
- Reviews: `/api/events/{id}/reviews/` and `/api/events/{id}/list_reviews/`

Run tests

```powershell
python manage.py test -v 2
```

CI

There is a GitHub Actions workflow at `.github/workflows/ci.yml` that runs the tests on push.

Notes

- Celery support is included (see `chaintech_project/celery.py` and `events/tasks.py`) but not required for tests. Configure a broker (Redis/RabbitMQ) to run background tasks.
- Configure `SECRET_KEY`, `DEBUG`, and production database settings before deploying.

Good luck with the assignment!
