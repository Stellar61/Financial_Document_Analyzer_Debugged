from celery import Celery

celery_app = Celery(
    "financial_analyzer",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0"
)

# Important: import tasks manually so Celery registers them
import tasks  # <-- THIS LINE FIXES EVERYTHING