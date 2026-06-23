#!/bin/bash

# Create and activate virtual environment
python3 -m venv .venv
source .venv/bin/activate

# Install Python dependencies
pip install -r requirements.txt

# Run database migrations
python manage.py migrate --noinput

# Create superuser if it doesn't exist
python create_superuser.py

# Collect static files
python manage.py collectstatic --noinput
