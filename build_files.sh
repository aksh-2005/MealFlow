#!/bin/bash

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate --noinput

# Create superuser if it doesn't exist
python create_superuser.py

# Collect static files
python manage.py collectstatic --noinput
