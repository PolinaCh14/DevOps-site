# DevOps-site

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