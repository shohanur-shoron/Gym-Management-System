# Gym Management System

A comprehensive Django-based gym management system with role-based access control, workout planning, and user management.

## Overview

This Gym Management System is a web application built with Django and Django REST Framework that enables efficient management of gym operations. The system includes features for user management, gym branch administration, workout planning, and task assignment.

## Features

- **Role-Based Access Control**: Four distinct user roles (Admin, Manager, Trainer, Member) with specific permissions
- **User Management**: Create, update, and manage users across different gym branches
- **Gym Branch Management**: Manage multiple gym locations with associated staff and members
- **Workout Planning**: Create and assign workout plans to members
- **Task Tracking**: Monitor member progress with workout task assignments
- **Activity Logging**: Track user activities for audit purposes
- **JWT Authentication**: Secure API access with JSON Web Tokens
- **API Documentation**: Built-in Swagger and ReDoc documentation
- **Celery Integration**: Background task processing for improved performance

## Architecture

The system consists of three main Django apps:

### Account App
- User authentication and authorization
- Profile management
- Activity logging
- Password management

### Gyms App
- Gym branch management
- Location and status tracking
- Branch-specific operations

### Workouts App
- Workout plan creation and management
- Task assignment to members
- Progress tracking

## Technology Stack

- **Backend**: Django 5.2.10, Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Documentation**: DRF-YASG for API documentation
- **Background Tasks**: Celery with Redis
- **Frontend API**: RESTful API endpoints
- **CORS**: Cross-origin resource sharing support

## User Roles & Permissions

- **Admin**: Super administrators with full access to all resources across all branches
- **Manager**: Gym managers with access to resources within their assigned branch
- **Trainer**: Fitness trainers who can create workout plans and assign tasks to members in their branch
- **Member**: Gym members who can view and update the status of their assigned workout tasks

## API Endpoints

The system provides comprehensive RESTful API endpoints for all operations. See the [API Documentation](API_Documentation.md) for detailed information about all available endpoints.

You can also access the interactive API documentation using the following link:
[Postman API Documentation](https://documenter.getpostman.com/view/37259871/2sBXVhDWbG)

## Installation & Setup

See the [Running Guide](RUNNING_GUIDE.md) for detailed instructions on setting up and running the application locally.

## Configuration

The application uses environment variables for configuration, managed through the `.env` file. Key configuration areas include:

- Database connection settings
- Email service configuration
- Redis/Celery settings
- Security settings (secret key, debug mode)

## Security Features

- JWT-based authentication
- Role-based permission system
- Input validation and sanitization
- Secure password storage
- Activity logging for audit trails

## Development

This project follows Django best practices and includes:

- Custom user model with role-based functionality
- Comprehensive serializer setup
- Proper API versioning considerations
- Clean, maintainable code structure


