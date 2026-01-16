# API Documentation

This document provides a comprehensive overview of all available API endpoints in the Gym Management System.

For an interactive API documentation experience, visit: [Postman API Documentation](https://documenter.getpostman.com/view/37259871/2sBXVhDWbG)

## Admin Login Information (Important)

For evaluation purposes, use the following admin credentials to access the system:

**Email**: admin@gmail.com
**Password**: 1324

This information is essential for accessing the APIs and evaluating the system functionality.

## Authentication

This API uses JWT (JSON Web Token) authentication. To access protected endpoints, include the access token in the Authorization header:

```
Authorization: Bearer <access_token>
```

## Base URL

All API endpoints are prefixed with `/api/v1/` (assuming standard Django REST Framework setup).

## API Endpoints

### Account Authentication & User Management

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| POST | `/auth/login/` | Authenticate user and obtain JWT tokens | Public |
| POST | `/auth/token/refresh/` | Refresh expired access token | Public |
| GET | `/auth/profile/` | Retrieve current user's profile | Authenticated |
| POST | `/auth/change-password/` | Change current user's password | Authenticated |
| GET | `/auth/activity-logs/` | List user's activity logs | Admin, Authenticated |
| GET | `/auth/users/` | List users based on role: Admin sees all, Manager sees branch users, Trainer sees branch members | Admin, Manager, Trainer |
| POST | `/auth/users/` | Create a new user | Admin |
| GET | `/auth/users/{id}/` | Retrieve specific user details | Admin, Manager |
| PUT | `/auth/users/{id}/` | Update specific user details | Admin, Manager |
| PATCH | `/auth/users/{id}/` | Partially update specific user details | Admin, Manager |
| DELETE | `/auth/users/{id}/` | Delete specific user | Admin, Manager |

### Gym Branch Management

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/gyms/branches/` | List all gym branches (with optional filtering) | Admin |
| POST | `/gyms/branches/create/` | Create a new gym branch | Admin |
| GET | `/gyms/branches/{id}/` | Retrieve specific gym branch details | Admin |
| PUT | `/gyms/branches/{id}/update/` | Update specific gym branch | Admin |
| PATCH | `/gyms/branches/{id}/update/` | Partially update specific gym branch | Admin |
| DELETE | `/gyms/branches/{id}/delete/` | Delete specific gym branch | Admin |

### Workout Plan Management

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/workouts/plans/` | List all workout plans (filtered by role/branch) | Admin, Trainer, Manager |
| POST | `/workouts/plans/` | Create a new workout plan | Trainer |
| GET | `/workouts/plans/{id}/` | Retrieve specific workout plan details | Admin, Trainer, Manager |
| PUT | `/workouts/plans/{id}/` | Update specific workout plan | Trainer |
| PATCH | `/workouts/plans/{id}/` | Partially update specific workout plan | Trainer |
| DELETE | `/workouts/plans/{id}/` | Delete specific workout plan | Trainer |

### Workout Task Management

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/workouts/tasks/` | List all workout tasks (filtered by role/branch) | Admin, Trainer, Manager, Member |
| POST | `/workouts/tasks/` | Create a new workout task | Trainer |
| GET | `/workouts/tasks/{id}/` | Retrieve specific workout task details | Admin, Trainer, Manager, Member |
| PUT | `/workouts/tasks/{id}/` | Update specific workout task | Trainer, Member (status only) |
| PATCH | `/workouts/tasks/{id}/` | Partially update specific workout task | Trainer, Member (status only) |
| DELETE | `/workouts/tasks/{id}/` | Delete specific workout task | Trainer |

### Documentation & Testing

| Method | Endpoint | Description | Roles |
|--------|----------|-------------|-------|
| GET | `/swagger/` | Interactive API documentation (Swagger UI) | Public |
| GET | `/redoc/` | Alternative API documentation (ReDoc) | Public |

## Role-Based Access Control

- **Admin**: Super administrators with full access to all resources
- **Manager**: Gym managers with access to resources within their branch
- **Trainer**: Fitness trainers with access to create workout plans, assign tasks within their branch, and view members in their branch
- **Member**: Gym members with access to view and update their own tasks

## Common Request/Response Formats

### Authentication Response
```json
{
  "refresh": "string",
  "access": "string",
  "role": "string",
  "gym_branch": "integer|null",
  "email": "string"
}
```

### User Object
```json
{
  "id": "integer",
  "email": "string",
  "role": "string",
  "first_name": "string|null",
  "last_name": "string|null",
  "phone_number": "string|null",
  "gender": "string|null",
  "gym_branch": "integer|null",
  "is_active": "boolean",
  "is_verified": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Gym Branch Object
```json
{
  "id": "integer",
  "name": "string",
  "location": "string",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Workout Plan Object
```json
{
  "id": "integer",
  "title": "string",
  "description": "text",
  "created_by": "integer",
  "gym_branch": "integer",
  "is_active": "boolean",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

### Workout Task Object
```json
{
  "id": "integer",
  "workout_plan": "integer",
  "member": "integer",
  "status": "string",
  "due_date": "date",
  "notes": "text|null",
  "completed_at": "datetime|null",
  "created_at": "datetime",
  "updated_at": "datetime"
}
```

## Error Responses

Common error responses include:

- `400 Bad Request`: Invalid request data
- `401 Unauthorized`: Missing or invalid authentication credentials
- `403 Forbidden`: Insufficient permissions to access the resource
- `404 Not Found`: Requested resource does not exist
- `500 Internal Server Error`: Unexpected server error