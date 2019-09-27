# Team Happiness

A Django REST Application to allow daily checkins and monitoring of your team's happiness

# Prerequisites

- Python 3.7

## Libraries
- django
- djangorestframework

# Setup
1. Create and activate virtualenv:
```
python3 -m venv venv && source venv/bin/activate
```
2. Install the project requirements:
```
pip install --upgrade pip && pip install -r requirements.txt
```

# Development Server
To test the development server locally.
1. Activate virtualenv:
```
source venv/bin/activate
```
2. Run database migrations:
```
python manage.py migrations
```
3. Create superuser:
```
python manage.py createsuperuser
```
4. Run development server:
```
python manage.py runserver
```
5. Add users via the admin by visiting [http://localhost:8000/admin/](http://localhost:8000/admin/) using the superuser account created
