# chaintech_project package
try:
	# Import Celery app when available so `celery -A chaintech_project` works
	from .celery import app as celery_app  # noqa: F401
except Exception:
	# Celery is optional for local test runs
	celery_app = None
