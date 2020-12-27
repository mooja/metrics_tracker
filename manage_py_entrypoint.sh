python3 manage.py makemigrations
python3 manage.py migrate
python3 manage.py collectstatic --no-input
gunicorn -b 0.0.0.0:8000 -w 4 metrics_tracker.wsgi:application