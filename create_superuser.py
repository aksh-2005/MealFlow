import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'MealFlow.settings')
django.setup()

from django.contrib.auth import get_user_model

def create_admin():
    User = get_user_model()
    username = os.environ.get('DJANGO_SUPERUSER_USERNAME', 'admin')
    email = os.environ.get('DJANGO_SUPERUSER_EMAIL', 'admin@example.com')
    password = os.environ.get('DJANGO_SUPERUSER_PASSWORD')
    
    if not password:
        print("DJANGO_SUPERUSER_PASSWORD environment variable is not set. Skipping superuser creation.")
        return

    if User.objects.filter(username=username).exists():
        print(f"Superuser '{username}' already exists.")
    else:
        User.objects.create_superuser(username=username, email=email, password=password)
        print(f"Superuser '{username}' created successfully.")

if __name__ == '__main__':
    create_admin()
