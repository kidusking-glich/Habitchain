release: python manage.py create_superuser && python manage.py migrate
web: gunicorn Habitchain.wsgi --preload
