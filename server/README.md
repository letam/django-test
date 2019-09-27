# Team Happiness

A Django REST Application to allow daily checkins and monitoring of your team's happiness

# One-step Demo Setup and Execution
With a single command, you can setup the project environment, run the test suites, load demo data, and run the development server:
```
./demo.sh
```

# Exploring the API
- Visit the web-browsable API at [http://localhost:8000/api/v1/happiness/](http://localhost:8000/api/v1/happiness/).

- Get the stats for a certain date by providing it in the URL in the form of `http://127.0.0.1:8000/api/v1/happiness/YYY-MM-DD/`.
  <br/> For example: [http://127.0.0.1:8000/api/v1/happiness/2019-09-27/](http://127.0.0.1:8000/api/v1/happiness/2019-09-27/)

- The demo fixture includes users named **super** (superuser account), **user2**, **user3**, **user4**, **user5**.
  <br/> The passwords for all accounts are **123**.

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
python manage.py migrate
```
3. Create superuser:
```
python manage.py createsuperuser
```
4. Run development server:
```
python manage.py runserver
```
5. You can add teams and users via the django admin interface by visiting [http://localhost:8000/admin/](http://localhost:8000/admin/) using the superuser account created. A user can be assigned to a team by changing their profile value at the bottom of their respective edit page.

# Demo data
Load demo data through the provided fixture:
```
python manage.py loaddata happiness_demo
```

# Automated Testing
To run automated tests for the project's apps:
```
python manage.py test apps
```
