
# 🚗 Car Insurance API (Django + Docker)

A modular backend system for managing car insurance data — built with **Django REST Framework**, **PostgreSQL**, **Redis**, and **Docker**.  
It provides endpoints for owners, cars, insurance policies, claims, and history tracking.

---

## 🧱 Architecture Overview

| Layer | Technology |
|-------|-------------|
| **Backend Framework** | Django 5 + Django REST Framework |
| **Database** | PostgreSQL (via Docker Compose) |
| **Cache / Task Queue** | Redis |
| **Email Testing** | MailHog |
| **Containerization** | Docker + Docker Compose |
| **Automation** | PowerShell scripts (`scripts/setup/*.ps1`) |

---

### 🗂 Project Structure

```

car_insurance/
├── apps/                     # Domain apps (cars, owners, policies, etc.)
├── core/                     # Cross-cutting utilities (health checks, tasks)
├── car_insurance/            # Django project config (settings, urls)
├── scripts/                  # PowerShell utilities
│   ├── setup/
│   │   ├── run.ps1           # Full environment setup
│   │   ├── db.ps1            # Database maintenance script
│   ├── cleanup.ps1           # Remove all containers & volumes
│   └── seed.ps1              # (Optional) Seed sample data
├── Dockerfile                # Backend image definition
├── docker-compose.yml        # Full stack (Django + Postgres + Redis + MailHog)
├── requirements.txt          # Python dependencies
├── .env                      # Environment variables (ignored in Git)
└── README.md

````

---

## 🧰 Prerequisites

Ensure the following are installed and running:

- **Docker Desktop** or **Rancher Desktop**  
  (Enable Docker socket exposure if using Rancher)
- **PowerShell** (Windows or cross-platform)
- **Ports availability:**
  - `8000` → Django
  - `5432` → PostgreSQL
  - `6379` → Redis
  - `8025` → MailHog

---

## ⚙️ Configuration

Create a `.env` file in the project root:

```ini
# Security
SECRET_KEY=supersecretkey
DEBUG=True

# Database
POSTGRES_DB=
POSTGRES_USER=
POSTGRES_PASSWORD=
POSTGRES_HOST=db
POSTGRES_PORT=5432

# Cache / Broker
REDIS_URL=redis://redis:6379/1

# Networking
ALLOWED_HOSTS=localhost,127.0.0.1
````

---

## 🚀 Getting Started

To build and start the full environment:

```powershell
.\scripts\setup\run.ps1
```

This script will:

1. Build Docker images
2. Start PostgreSQL, Redis, and MailHog
3. Run migrations and apply schema updates
4. Automatically create an admin user
5. Start Django at [http://localhost:8000](http://localhost:8000)

**Admin credentials:**

```
username: admin
password: admin123
```

---

## 🩺 Health Check

Visit:

```
http://localhost:8000/health
```

Expected response:

```json
{
  "status": "ok",
  "database": "ok",
  "cache": "ok"
}
```

---

## 🧠 API Example – Cars

| Method   | Endpoint          | Description    |
| -------- | ----------------- | -------------- |
| `GET`    | `/api/cars/`      | List cars      |
| `POST`   | `/api/cars/`      | Create a car   |
| `GET`    | `/api/cars/{id}/` | Retrieve a car |
| `PUT`    | `/api/cars/{id}/` | Update a car   |
| `DELETE` | `/api/cars/{id}/` | Delete a car   |

**Example POST Payload**

```json
{
  "vin": "WVWZZZ1JZXW000001",
  "make": "Volkswagen",
  "model": "Golf",
  "year_of_manufacture": 2018
}
```

---

## 🧩 PowerShell Scripts

| Script                  | Description                                                        |
| ----------------------- | ------------------------------------------------------------------ |
| `scripts/setup/run.ps1` | Builds and runs the full Docker stack (auto-migrate + admin setup) |
| `scripts/setup/db.ps1`  | Manage migrations, backups, and restores                           |
| `scripts/seed.ps1`      | (Optional) Seed initial or test data                               |
| `scripts/cleanup.ps1`   | Stop and remove containers and volumes                             |
| `scripts/scheduler.ps1` | Run background tasks or policy expiry detection manually           |

---

## 📧 MailHog

MailHog captures all outbound emails for testing.

* UI: [http://localhost:8025](http://localhost:8025)
* SMTP: `mailhog:1025`

---

## 🧹 Useful Commands

**Rebuild everything:**

```powershell
.\scripts\setup\run.ps1 -Rebuild
```

**Apply migrations manually:**

```powershell
docker compose exec backend python manage.py makemigrations
docker compose exec backend python manage.py migrate
```

**Django shell:**

```powershell
docker compose exec backend python manage.py shell
```

**Check containers:**

```powershell
docker compose ps
```

---

## 🧾 Environment URLs

| Service      | URL                                                          |
| ------------ | ------------------------------------------------------------ |
| Django API   | [http://localhost:8000](http://localhost:8000)               |
| Django Admin | [http://localhost:8000/admin/](http://localhost:8000/admin/) |
| MailHog      | [http://localhost:8025](http://localhost:8025)               |
| PostgreSQL   | `localhost:5432`                                             |
| Redis        | `localhost:6379`                                             |

---

## 🧱 Default Database Schema

| Table              | Description                                  |
| ------------------ | -------------------------------------------- |
| `cars_car`         | Stores vehicle data (VIN, make, model, year) |
| `auth_user`        | Django user accounts (includes admin)        |
| `django_session`   | Session management                           |
| `django_admin_log` | Admin audit trail                            |

---

## 🧠 Developer Notes

* All scripts are **idempotent** — rerunning them won’t break or duplicate setup.
* `run.ps1` auto-applies any pending model migrations at startup.
* Admin credentials are recreated on each rebuild for consistency.

---

## 📜 License

For internal or educational use.
Extend, fork, or deploy freely for production under your organization’s policies.

---

## 🧾 .gitignore (Recommended)

```
# Python
__pycache__/
*.py[cod]
*.pyo
*.pyd
*.pyc
*.pdb
*.egg-info/

# Django
db.sqlite3
*.log
*.pot
*.pydevproject
.env
.env.local
.env.*.local
.vscode/
.idea/
media/
staticfiles/

# Docker
*.pid
docker-compose.override.yml

# OS
.DS_Store
Thumbs.db

# Virtual environments
venv/
.env/
.venv/
Scripts/
