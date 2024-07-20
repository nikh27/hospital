# Django Hospital Project

This is a simple hospital management application built using Django.

## Deployment

The project is deployed and can be accessed at: [Django Hospital Project](https://nikh27.pythonanywhere.com/)

## Demo video
[video 1](https://drive.google.com/file/d/1aCtSvAhmaDWQMvUM9p3LC2csvlYXV_Nd/view?usp=sharing)
[video 2](https://drive.google.com/file/d/1QzYvLGdTGPjBR0s-qUk16AArFOZHQGPP/view?usp=sharing)

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