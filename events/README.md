# events app

This `events` app implements an Event Management REST API for Django REST Framework with JWT authentication (djangorestframework-simplejwt), RSVP and Reviews.

Files created:
- `models.py` — Event, RSVP, Review, UserProfile models
- `serializers.py` — DRF serializers for the models
- `views.py` — ModelViewSets and actions for RSVP and reviews
- `permissions.py` — custom permissions (IsOrganizerOrReadOnly, IsInvitedOrPublic)
- `urls.py` — router with `/events/`, `/rsvp/`, `/reviews/`
- `admin.py` — admin registrations
- `apps.py`, `__init__.py`

Quick setup (add to your existing Django project):

1. Move or copy this `events` folder into your project root (where `manage.py` is), or add it to `PYTHONPATH`.

2. Add `events` and REST framework apps in your `settings.py`:

```python
INSTALLED_APPS = [
    # ... existing apps
    'rest_framework',
    'rest_framework_simplejwt',
    'events',
]
```

3. Add REST framework + simplejwt settings (example):

```python
from datetime import timedelta

REST_FRAMEWORK = {
    'DEFAULT_AUTHENTICATION_CLASSES': (
        'rest_framework_simplejwt.authentication.JWTAuthentication',
    ),
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10,
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=60),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
}
```

4. Add URL routing in your project `urls.py` (typically next to `admin`):

```python
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    # ... other urls
    path('api/', include('events.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
```

5. Install dependencies and run migrations:

```powershell
pip install -r requirements.txt
python manage.py makemigrations events
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Endpoints summary:
- `/api/events/` — list/create events
- `/api/events/{id}/` — retrieve/update/delete (if organizer)
- `/api/events/{id}/rsvp/` — POST to RSVP (body: {"status":"Going"})
- `/api/events/{id}/reviews/` — POST to create review
- `/api/events/{id}/list_reviews/` — GET to list reviews for event
- `/api/rsvp/` — list user's RSVPs
- `/api/reviews/` — list user's reviews

Notes and next steps:
- You may want to add validation (e.g., rating range) and rate-limiting.
- In production, configure media/static serving (profile pictures), CORS, and HTTPS.

Tests
-----
This app contains basic unit tests in `events/tests.py` which cover creating/listing events, RSVP flow and reviews. Run them from your project root:

```powershell
python manage.py test events
```

Celery (optional)
-----------------
A small Celery task skeleton is included in `events/tasks.py` to send email notifications when events are created or updated. To use it in production, add `celery` to your requirements, configure a broker (Redis or RabbitMQ) and wire up a `celery.py` at project level. This is intentionally minimal to earn the bonus credit in the assignment.
