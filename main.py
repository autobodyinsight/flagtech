# Import the app from app/main.py to make it accessible at the root level
# This allows gunicorn to import it as 'main:app'
from app.main import app

__all__ = ['app']
