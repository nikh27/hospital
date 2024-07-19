# Django Hospital Project

This is a simple hospital management application built using Django.

## Deployment

The project is deployed and can be accessed at: [Django Hospital Project](https://nikh27.pythonanywhere.com/)

## Project Structure

hospital/
├── hospital/
│ ├── pycache/
│ ├── init.py
│ ├── asgi.py
│ ├── settings.py
│ ├── urls.py
│ ├── wsgi.py
├── user/
│ ├── pycache/
│ ├── migrations/
│ ├── templates/
│ ├── init.py
│ ├── admin.py
│ ├── apps.py
│ ├── forms.py
│ ├── models.py
│ ├── tests.py
│ ├── urls.py
│ ├── views.py
├── db.sqlite3
├── manage.py
├── requirements.txt
├── .gitignore
└── README.md


## Features

- User authentication (signup/login)
- Different user roles (Patient and Doctor)

## Setup

1. Clone the repository:

```sh
git clone <repository_url>
cd hospital


python -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
pip install -r requirements.txt


python manage.py migrate
python manage.py runserver