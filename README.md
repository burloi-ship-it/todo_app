# ✅ Post-A-Todo

![Python](https://img.shields.io/badge/Python-3.12-blue?logo=python&logoColor=white)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-009688?logo=fastapi&logoColor=white)
![SQLAlchemy](https://img.shields.io/badge/SQLAlchemy-ORM-red?logo=sqlalchemy&logoColor=white)
![Bootstrap](https://img.shields.io/badge/Bootstrap-5.3-7952B3?logo=bootstrap&logoColor=white)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED?logo=docker&logoColor=white)

A full-stack, secure, and responsive task management and blogging web application built with **FastAPI**, **SQLAlchemy**, **Jinja2**, and **Bootstrap 5**. Designed with RESTful principles, complete authentication workflows, email notifications, and Docker support.

---

## ✨ Key Features

* **🔐 Secure Authentication & Authorization**:
  * User registration and login powered by **JWT (JSON Web Tokens)** stored securely in HTTP-only cookies.
  * Industry-standard password hashing using **Argon2**.
  * Complete **Password Management**: Authenticated password updates (`/change-password`) and secure token-based email password recovery (`/forgot-password` & `/reset-password`) integrated via **Resend**.
* **📋 Task & Note Management (RESTful API + SSR)**:
  * Create, read, update (`PATCH`), and delete (`DELETE`) tasks seamlessly without page reloads via Fetch API.
  * **Interactive Calendar Filtering**: Visual monthly calendar highlighting dates with scheduled tasks and allowing instant date-based filtering.
  * Real-time progress bar tracking task completion rates.
  * Dedicated detailed view for individual tasks/notes (`/task/{id}`).
* **🎨 Modern, Responsive UI**:
  * Unified **Bootstrap 5.3** interface with **Bootstrap Icons**.
  * Built-in **Dark / Light Mode** toggle persisted in `localStorage`.
* **🗄️ Database & Migrations**:
  * Powered by **SQLAlchemy** ORM with **Alembic** configured for schema migrations.
* **🐳 Containerized Deployment**:
  * Ready for deployment with included `Dockerfile` and `docker-compose.yml`.

---

## 🛠️ Tech Stack

* **Backend**: Python 3.12, FastAPI, Uvicorn
* **Database & ORM**: SQLite (default) / PostgreSQL ready, SQLAlchemy, Alembic
* **Frontend**: Jinja2 Templates, Bootstrap 5.3, Vanilla JavaScript (ES6+ Fetch API)
* **Security & Email**: Passlib (Argon2), Python-JOSE (JWT), Resend API
* **DevOps**: Docker, Docker Compose

---

## 📂 Project Structure

```text
postatodo/
├── alembic/                 # Database migration scripts and configuration
├── routers/
│   ├── auth.py              # Authentication, registration, and password reset routes
│   └── tasks.py             # Task CRUD endpoints (HTML views + REST API)
├── static/
│   ├── css/style.css        # Custom styling and Dark Mode overrides
│   └── images/logo.png      # Application branding assets
├── templates/               # Jinja2 HTML templates extending layout.html
│   ├── layout.html          # Base template with navbar, footer, and theme switcher
│   ├── home.html            # Dashboard with interactive calendar and task list
│   ├── task.html            # Detailed task/post view
│   ├── login.html           # User login page
│   ├── register.html        # User registration page
│   ├── change_password.html # Authenticated password update form
│   ├── forgot_password.html # Password recovery request form
│   ├── reset_password.html  # Token-verified new password form
│   └── error.html           # Custom error handling page
├── database.py              # SQLAlchemy engine and session management
├── email_service.py         # Resend email integration for password recovery
├── main.py                  # FastAPI application entry point and middleware
├── models.py                # SQLAlchemy database models (User, Task)
├── schemas.py               # Pydantic validation schemas
├── security.py              # Argon2 hashing and JWT token utilities
├── Dockerfile               # Docker image build instructions
├── docker-compose.yml       # Multi-container orchestration setup
└── requirements.txt         # Python dependencies


<img width="1918" height="1016" alt="login" src="https://github.com/user-attachments/assets/50fef0a0-62e2-4485-b846-8c6761f51f14" />

<img width="1917" height="1017" alt="dashborad" src="https://github.com/user-attachments/assets/4a9944f1-126f-4062-8ef3-361c0b874be5" />

<img width="1918" height="1016" alt="edit_task" src="https://github.com/user-attachments/assets/5ece2715-868f-4935-a255-652664edecb7" />

<img width="1918" height="1011" alt="change_password" src="https://github.com/user-attachments/assets/b3adb663-e7cb-466d-a10f-e7773825c8f8" />

<img width="1918" height="1012" alt="forgot_password" src="https://github.com/user-attachments/assets/3f479246-d071-4719-b453-9b45c2158afa" />

<img width="1918" height="1017" alt="darkmode" src="https://github.com/user-attachments/assets/1a4172c7-354d-45e0-9775-4386dd67b32c" />





