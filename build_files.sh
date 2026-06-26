#!/bin/bash
# Install dependencies
pip install -r requirements.txt

# Collect static files into STATIC_ROOT (staticfiles)
python manage.py collectstatic --noinput --clear
