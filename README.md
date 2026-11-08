# DevOps-site

## Docker and CI

The repository root contains the Docker Compose configuration; the Django project
and `manage.py` are under `devopssite/`.

### Start the application

Install Docker Desktop (or Docker Engine with the Compose plugin). Create a
local environment file from the example if you do not already have one, then
set the required local-only values:

```powershell
if (-not (Test-Path .env)) { Copy-Item .env.example .env }
```

Required variables are `DB_NAME`, `DB_USER`, `DB_PASSWORD`, and
`DJANGO_SECRET_KEY`. The example values are for local development only and
must not be used in production. Docker Compose supplies the database and Redis
service hostnames to Django; `WEB_PORT` can optionally change the host port
(default `8000`).

Build and start Django, PostgreSQL, and Redis:

```powershell
docker compose up --build -d
```

Open [http://localhost:8000](http://localhost:8000). The PostgreSQL service is
available only on the private Compose network; its data persists in the named
`postgres_data` volume.

### Migrations and tests

Run database migrations and the existing Django test suite inside the app
container:

```powershell
docker compose exec web python manage.py migrate
docker compose exec web python manage.py test
```

Run Django's system checks with:

```powershell
docker compose exec web python manage.py check
```

### Stop containers

Stop and remove containers while retaining the PostgreSQL data volume:

```powershell
docker compose down
```

To also delete the local PostgreSQL data volume:

```powershell
docker compose down --volumes
```

GitHub Actions runs these same Docker-based checks on every push and on pull
requests when opened, synchronized, or reopened. It starts isolated PostgreSQL
and Redis services, runs Django checks, applies migrations, executes the
automated test suite, and removes its containers and volumes afterward. CI
uses disposable test credentials and never connects to a non-CI database.

## Setup

This repository is organized as a Django project under the `devopssite/` directory. The app entry point is `devopssite/manage.py`, and environment configuration is provided by `env_example` and the local `.env` file.

### Prerequisites
- Python 3 installed on the machine
- Access to the repository root: `D:\piton\practice\DevOps-site`

### 1) Create and activate a virtual environment
From the repository root:

```powershell
cd D:\piton\practice\DevOps-site
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### 2) Install Python dependencies
Use the project dependency file instead of installing packages manually:

```powershell
python -m pip install --upgrade pip
pip install -r requirements.txt
```

### 3) Configure environment variables
Copy the example environment file and fill in the required values for the local database and Django settings:

```powershell
Copy-Item env_example .env
```

Then update `.env` with the values required by `devopssite/devopssite/settings.py`, including:
- `DB_NAME`
- `DB_USER`
- `DB_PASSWORD`
- `DB_HOST`
- `DB_PORT`
- `DJANGO_SECRET_KEY`
- email-related settings if you plan to send mail locally

### 4) Apply database migrations
The Django project lives in `devopssite/`, so run migrations from that directory:

```powershell
cd devopssite
python manage.py migrate
```

### 5) Run the project locally
```powershell
python manage.py runserver
```

The app should then be available through the local Django development server, which typically serves the project on `http://127.0.0.1:8000/`.

### Repository structure relevant to setup
- `devopssite/manage.py` — Django project entry point
- `devopssite/devopssite/settings.py` — Django settings and environment loading
- `devopssite/devopssite/urls.py` — root URL configuration
- `devopssite/templates/` — HTML templates
- `devopssite/static/` — frontend static assets
- `devopssite/` — application modules such as `users`, `project`, `chat`, `freelancer`, `rating`, `notification`, and `workrequest`
- `requirements.txt` — current Python dependency set
- `env_example` and `.env` — environment configuration

This setup is based on the current repository structure and does not modify any application code.