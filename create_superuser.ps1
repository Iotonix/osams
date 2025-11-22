$env:DJANGO_SUPERUSER_USERNAME = "admin"
$env:DJANGO_SUPERUSER_EMAIL = "ralf@ait.co.th"
$env:DJANGO_SUPERUSER_PASSWORD = "admin123"

python manage.py createsuperuser --noinput