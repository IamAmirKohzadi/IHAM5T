# IHAM5T - Advanced Blog Management System
Advanced Blog Management System with User Authentication and Content Recommendation

## Overview
IHAM5T is a full-stack blog and news platform developed as a bachelor diploma project at the University of Pecs.
It provides secure user authentication, blog content management, social interactions, and rule-based content discovery
through a REST API built with Django 5 and Django REST Framework (DRF).

The project uses a modular Django architecture, automated tests, API documentation, performance testing, and a
containerized development environment.

## Main Features
- User registration, login, and authentication using JWT
- Role-based access control and email verification
- Blog post creation, editing, and deletion
- Categories, comments, reactions, and reports
- Social features (friends and friend requests)
- Rule-based content discovery (popular posts, top authors, category filtering)
- REST API for all core features
- API documentation using Swagger (OpenAPI)
- Automated tests
- Performance testing with Locust
- Dockerized development environment

## Technology Stack
Backend
- Python 3.11
- Django 5.2
- Django REST Framework (DRF)
- Simple JWT
- SQLite (default development database)
- mail_templated
- django-filter
- drf-yasg

DevOps and Tools
- Docker and Docker Compose
- Locust (load testing)
- SMTP4Dev (email testing)

## Configuration
Create a `.env` file in the project root based on `.env.example` and fill in your own keys.
These values are intentionally not committed to GitHub.

## Project Structure
```
IHAM5T/
  core/
    core/
    accounts/
      api/
      models/
      templates/
      test/
    blog/
      api/
      management/
      templates/
      test/
    friends/
      api/
      templates/
      test/
    website/
      templates/
      static/
      test/
    templates/
    staticfiles/
    manage.py
  docker-compose.yml
  dockerfile
  requirements.txt
  README.md
```

## API Structure
Each Django app exposes a dedicated REST API module.

Accounts API (accounts/api/v1)
- User registration and authentication
- JWT token generation and verification
- Profile management and password change

Blog API (blog/api/v1)
- Blog post CRUD operations
- Categories and content organization
- Comments, reactions, and reports
- Popular content discovery and top author

Friends API (friends/api/v1)
- Friend requests and approvals
- Friendship listing and removal

All APIs return JSON responses and follow REST principles.

## Running the Project (Docker - Recommended)
Start the containers:
```
docker compose up --build
```

Ensure `.env` exists in the project root so Docker injects environment variables.

Apply database migrations:
```
docker compose exec backend python manage.py makemigrations
```
```
docker compose exec backend python manage.py migrate
```

Create a superuser:
```
docker compose exec backend python manage.py createsuperuser
```

Backend will be available at:
http://localhost:8000

SMTP4Dev (email testing) will be available at:
http://localhost:5000

## Running Locally (Without Docker)
Create and activate a virtual environment:
```
python -m venv venv
venv\Scripts\activate
```

Install dependencies:
```
pip install -r requirements.txt
```

Apply migrations:
```
python manage.py makemigrations
```
```
python manage.py migrate
```

Run the development server:
```
python manage.py runserver
```

## Dummy Data (Faker Seed)
Generate sample users, categories, and posts:
```
python manage.py insert_data
```

Docker (seed data inside container):
```
docker compose exec backend python manage.py insert_data
```

## Performance Testing (Locust)
This project includes Locust services in Docker Compose:
- master (Locust web UI)
- worker (load generator)

Start Locust master and worker:
```
docker compose up master worker
```

Locust UI will be available at:
http://localhost:8089

## Running Tests
Run all tests:
```
python manage.py test
```

Test coverage includes:
- Authentication and authorization
- Blog content management
- Social features and interactions

## API Documentation
Swagger UI endpoints (admin restricted):
- /swagger/
- /redoc/

These interfaces document and test all REST API endpoints for frontend integration.


## Academic Context
- Degree: Computer Science Engineering BSc  
- University: University of Pécs  
- Faculty: Engineering and Information Technology  
- Supervisor: Lénárt Anett  
- Academic Year: 2025/2026  

This project was developed as part of the bachelor diploma thesis requirements said above.
