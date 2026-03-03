web: gunicorn config.wsgi:application --bind 0.0.0.0:8080 --workers 2
release: python manage.py migrate
