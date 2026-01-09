# IHAM5T – Advanced Blog Management System
**Advanced Blog Management System with User Authentication and Content Recommendation**

## 📌 Overview
IHAM5T is a full-stack **blog management system** developed as a **Bachelor Diploma Project** at the **University of Pécs**.
The system provides secure user authentication, blog content management, social interactions, and rule-based content discovery features through a **RESTful API** built with **Django 5** and **Django REST Framework (DRF)**.

The project follows modern backend engineering practices, including modular architecture, token-based authentication, API documentation, automated testing, performance testing, and containerized deployment.

---

## ✨ Main Features
- User registration, login, and authentication using JWT
- Role-based access control
- Blog post creation, editing, and deletion
- Categories, comments, reactions (likes), and reports
- Social features (friends and follow system)
- Rule-based content discovery (popular posts, top authors, category filtering)
- RESTful API for all core features
- API documentation using Swagger (OpenAPI)
- Automated tests
- Performance testing with Locust
- Dockerized development environment

---

## 🧰 Technology Stack
**Backend**
- Python 3
- Django 5
- Django REST Framework (DRF)
- Simple JWT
- PostgreSQL
- Redis

**DevOps & Tools**
- Docker & Docker Compose
- Locust (load testing)
- SMTP4Dev (email testing)
- Swagger / OpenAPI (drf-yasg)

---

## 🏗️ Project Architecture
The project follows a **modular Django architecture**, where each major feature is implemented as a separate app with its own API layer.

---

## Core Project Tree
IHAM5T/
├── core/
│   ├── api/
│   ├── settings.py
│   ├── urls.py
│   └── locust/
├── accounts/
│   ├── api/
│   └── tests/
├── blog/
│   ├── api/
│   └── tests/
├── friends/
│   ├── api/
│   └── tests/
├── website/
├── docker-compose.yml
├── Dockerfile
├── requirements.txt
└── manage.py


---


## 🔌 API Structure
Each Django app exposes a dedicated REST API module.

### 🔐 Accounts API (`accounts/api/`)
- User registration and authentication
- JWT token generation
- User profile management

### 📝 Blog API (`blog/api/`)
- Blog post CRUD operations
- Categories and content organization
- Comments and reactions
- Popular content discovery

### 👥 Friends API (`friends/api/`)
- Friend requests
- Follow and unfollow functionality
- Social interactions

All APIs return JSON responses and follow REST principles.

---

## ⚙️ Environment Configuration
Create a `.env` file in the project root with the required environment variables:

```env
SECRET_KEY=your-secret-key
DEBUG=True

POSTGRES_DB=iham5t
POSTGRES_USER=postgres
POSTGRES_PASSWORD=postgres
POSTGRES_HOST=db
POSTGRES_PORT=5432

REDIS_HOST=redis
REDIS_PORT=6379


---


## 🐳 Running the Project (Docker – Recommended)
The recommended way to run the project is using Docker and Docker Compose.

Start the containers:
```bash
docker-compose up --build
Apply database migrations:docker-compose exec backend python manage.py makemigrations/migrate
Create a superuser (inside the backend service):docker-compose exec backend python manage.py createsuperuser
Backend will be available at:http://localhost:8000
SMTP4Dev (email testing) will be available at:http://localhost:5000


---


🖥️ Running Locally (Without Docker):
To run the project locally without Docker,Create and activate a virtual environment:
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
Install dependencies:pip install -r requirements.txt
Apply migrations:python manage.py makemigrations/migrate
Run the development server:python manage.py runserver



---


## 🚀 Performance Testing (Locust)
This project includes Locust services in Docker Compose:
- `master` (Locust web UI)
- `worker` (load generator)
Locust configuration file:core/locust/locustfile.py

Start Locust master + worker:
```bash
docker-compose up master worker
Backend will be available at:http://localhost:8089


---

🧪 Running Tests
Automated tests are implemented for each application module.
Run all tests using:python manage.py test
Test coverage includes:
-User authentication and authorization
-Blog content management
-Social features and interactions


---

📚 API Documentation
Interactive API documentation is available using Swagger (OpenAPI).
Swagger UI endpoints(admin restricted):
-/swagger/
-/redoc/
These interfaces provide detailed documentation and testing capabilities for all REST API endpoints for frontend developments!




