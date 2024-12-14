# fest-backend

Backend for the FEST project, built with Django and Django REST Framework.

## Features

## Requirements

- Python 3.12+
- Django 5.1.3
- PostgreSQL (recommended for production)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/festival-platform/fest-backend.git
   cd fest-backend
2.	Create and activate a virtual environment:
    ```bash
    python3 -m venv venv
    source venv/bin/activate
3.	Install dependencies:
    ```bash
    pip install -r requirements.txt
4.	Set up the environment variables:
Create a .env file in the root directory and define variables:
    ```bash
    # Django settings
    SECRET_KEY=KEY
    DEBUG=True
    ALLOWED_HOSTS=localhost,127.0.0.1

    # PostgreSQL settings
    POSTGRES_HOST=localhost
    POSTGRES_NAME=DB_NAME
    POSTGRES_USER=USER
    POSTGRES_PASSWORD=PASSWORD
    POSTGRES_PORT=5432
5.	Apply migrations:
    ```bash
    python manage.py migrate
6.	Run the development server:
    ```bash
    python manage.py runserver