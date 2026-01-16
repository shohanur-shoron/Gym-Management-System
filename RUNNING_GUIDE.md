# Gym Management System - Setup and Running Guide

This guide explains how to set up and run the Gym Management System locally.

## Admin Login Information (Important)

For evaluation purposes, use the following admin credentials to access the system:

**Email**: admin@gmail.com
**Password**: 1234

This information is essential for accessing the APIs and evaluating the system functionality.

## Prerequisites

Before you begin, ensure you have the following installed on your system:

- Python 3.8 or higher
- PostgreSQL database server
- Redis server (for Celery)
- pip (Python package installer)

## Installation Steps

### 1. Clone or Download the Project

If you're cloning from a repository:
```bash
git clone <repository-url>
cd <project-directory>
```

### 2. Create a Virtual Environment

It's recommended to use a virtual environment to isolate project dependencies:

```bash
python -m venv venv
```

Activate the virtual environment:

On Windows:
```bash
venv\Scripts\activate
```

On macOS/Linux:
```bash
source venv/bin/activate
```

### 3. Install Dependencies

Install all required packages using pip:

```bash
pip install -r requirements.txt
```

### 4. Set Up Environment Variables

Copy the `.env` file and adjust the values as needed for your local environment:

```bash
# Make sure to update these values in your .env file as needed
```

The project uses a `.env` file for configuration. Key variables include:

- `SECRET_KEY`: Django secret key for cryptographic signing
- `DEBUG`: Set to `True` for development, `False` for production
- `ALLOWED_HOSTS`: Host/domain names that Django can serve
- `DB_NAME`, `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT`: PostgreSQL database credentials
- `REDIS_URL`: Redis connection URL for Celery
- Email configuration variables for sending emails

### 5. Database Setup

Make sure PostgreSQL is running on your system. Then:

1. Create the database specified in your `.env` file
2. Run migrations to set up the database tables:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 6. Create a Superuser (Optional but Recommended)

Create an admin user to access the Django admin panel:

```bash
python manage.py createsuperuser
```

Follow the prompts to set username, email, and password.

### 7. Collect Static Files (For Production)

If deploying to production:

```bash
python manage.py collectstatic
```

## Running the Application

### 1. Start the Development Server

```bash
python manage.py runserver
```

By default, the server will run on `http://127.0.0.1:8000/`.

### 2. (Optional) Start Celery Worker

If your application uses background tasks, you'll need to start a Celery worker:

```bash
celery -A CORE worker -l info
```

### 3. (Optional) Start Celery Beat (Scheduler)

If you have scheduled tasks:

```bash
celery -A CORE beat -l info
```

### 4. Access the Application

- Main application: `http://127.0.0.1:8000/`
- Admin panel: `http://127.0.0.1:8000/admin/`
- API Documentation (Swagger): `http://127.0.0.1:8000/swagger/`
- API Documentation (ReDoc): `http://127.0.0.1:8000/redoc/`

## Important Notes

- Make sure PostgreSQL is running before starting the application
- Make sure Redis is running if using Celery for background tasks
- Update the `.env` file with appropriate values for your environment
- The JWT access tokens expire after 5 minutes, with refresh tokens lasting 1 day
- CORS is enabled for all origins in development (configured in settings.py)

## Troubleshooting

### Common Issues:

1. **Database Connection Error**: Ensure PostgreSQL is running and credentials in `.env` are correct
2. **Module Import Errors**: Make sure all dependencies are installed in your virtual environment
3. **Port Already in Use**: Change the port with `python manage.py runserver 8001`
4. **Permission Errors**: Ensure you're running commands from the correct project directory

### Useful Commands:

- Run tests: `python manage.py test`
- Check for potential issues: `python manage.py check`
- Open Django shell: `python manage.py shell`
- Create new migration after model changes: `python manage.py makemigrations`
- Apply migrations: `python manage.py migrate`

## API Access

Once the server is running, you can access the API endpoints as documented in the API documentation. The application includes JWT-based authentication and role-based access control.
