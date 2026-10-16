# CLAUDE.md

Guidance for Claude Code (and humans) working in this repository. [README.md](README.md) is the
user-facing page (deployment with the published image, environment variables, Grafana).

## What this is

Api Watch Tower (AWT) is a Django 3.2 application that monitors HTTP APIs. A `HealthCheckRule`
describes a call (URL, GET or POST, headers, body, optional client certificate) and what a healthy
answer looks like (regular expressions for the status code and the body). A Celery task calls every
enabled rule and stores a `HealthCheckRecord` per call (curl-style request, status, body, latency,
success, error) in PostgreSQL, where Grafana dashboards read them. The only UI is the Django admin,
themed with django-jet2, with optional Azure AD sign-in through `django-azure-ad-auth`. Redis is the
Celery broker and result backend, and also holds the variables used by `{{placeholders}}`.

## Commands

```bash
docker compose up -d --build           # postgres, redis, web (:8000), celery, celery-beat, grafana (:3000)
docker compose logs -f celery          # task output

# Without Docker for the app (the image uses Python 3.7; the pinned packages support up to 3.10)
pip install -r requirements.txt        # django-azure-ad-auth installs from GitHub, so git is needed
docker compose up -d postgres redis    # docker-compose.yml publishes 5432 and 6379
export AWT_PG_HOST=localhost AWT_REDIS_HOST=localhost
python manage.py migrate auth && python manage.py migrate   # this order matters (see gotchas)
python manage.py runserver 0.0.0.0:8000
celery -A ApiWatchTower worker -B --concurrency=10
celery -A ApiWatchTower beat -l info -S django --pidfile=
python manage.py check                 # quick sanity check, needs no database
python manage.py collectstatic         # after changing static assets (static/ is committed)
```

There is no real test suite: `HealthChecker/tests.py` is the template placeholder, and
`python manage.py test` fails while building the test database (the migration-order problem below).

## Layout

```
ApiWatchTower/            Django project
  settings.py             all settings; env vars via get_env_settings.get_env_value(name, default)
  celery.py               Celery app (CELERY_* settings, autodiscovers tasks)
  urls.py                 / -> /admin/, admin, jet, azure/ + /login/ + /complete/ (Azure AD), /static/, /media/
HealthChecker/            the only app
  models.py               HealthCheckRule, HealthCheckRecord, Header, ClientCertificate, EnvironmentVariable
  tasks.py                check_health, run_head_sync, make_http_call, clean_record, placeholder helpers
  admin.py                admin pages; Enable / Disable / Duplicate actions on rules
  apps.py                 post_migrate hook that creates the `members` and `admins` groups
  migrations/             0009 is a data migration that creates the first superuser
  static/                 logo and favicon (collectstatic source)
templates/admin/          base_site.html (branding), login.html (adds the "Azure AD Login" button)
static/                   collectstatic output (admin, jet, logo), committed and served by Django
code/static/              byte-identical copy of static/; nothing references it
certificates/             upload folder for client certificates (git-ignored except info.md; mount a volume)
grafana-*-dashboard.json  Grafana dashboards that query the HealthChecker tables
Dockerfile                python:3.7, copies the repo to /code, installs requirements; no CMD
docker-compose.yml        local stack built from source (the README has the published-image variant)
ApiWatchTower.pyproj      Visual Studio (PTVS) project file
```

## How a check runs

- Nothing is scheduled in code. Periodic tasks are created in the admin (django_celery_beat):
  `HealthChecker.tasks.check_health` at the wanted interval, and optionally
  `HealthChecker.tasks.clean_record` with the number of days to keep as its argument. Only the
  `beat -S django` process runs them; the worker's `-B` embedded beat uses Celery's file scheduler.
- `check_health` queues every enabled rule. Rules linked by `run_after` form chains: the head runs
  first through `run_head_sync`, which waits for the call (`.get(disable_sync_subtasks=False)`)
  and then queues the rules that point to it. Each waiting chain holds a worker slot, so keep
  `--concurrency` above the number of chains. A disabled rule in a chain is skipped, but the rules
  after it still run.
- `{{name}}` in the URL, header values and request body is replaced with key `name` from Redis
  db 1 (`None` if missing). Values come from `EnvironmentVariable` rows (written to Redis on save,
  removed on delete) and from a rule's `output_variables`: comma-separated JSON keys, `a__b` walks
  into nested objects, `key=>name` stores the value under another name.
- A JSON response is stored and matched as `json.dumps(..., sort_keys=True)`; anything else as the
  Python bytes repr (`b'...'`). The expected body is normalised the same way if it parses as JSON,
  then used as a regex (an escaped literal if it does not compile). The status-code regex is
  unanchored. Any exception is stored as a failed record with its message.

## Configuration

Environment variables, read in `settings.py` (a variable with no default raises ImproperlyConfigured):

- `AWT_PG_DBNAME`, `AWT_PG_USERNAME`, `AWT_PG_PASSWORD`, `AWT_PG_HOST`, `AWT_PG_PORT`: PostgreSQL.
- `AWT_REDIS_HOST`, `AWT_REDIS_PORT`: Celery broker/results (db 0) and placeholder store (db 1).
- `AWT_LANGUAGE_CODE` (default `it`), `AWT_TIME_ZONE` (default `Europe/Rome`).
- `AAD_TENANT_ID`, `AAD_CLIENT_ID`, `AAD_RESPONSE_TYPE`, `AAD_EMAIL_FIELD`: Azure AD sign-in. The
  mappings are fixed in settings: AAD users get `is_staff` and join `members`, and a `groups`
  claim value `admin` adds them to `admins`.
- `HTTPS` (`on`/`off`): stored in settings, but nothing reads that setting. It takes effect because
  `runserver` (wsgiref) copies the process environment into each request's WSGI environ, where
  `HTTPS=on` makes Django build https URLs (the Azure AD redirect URI behind a TLS proxy).
- `AWT_ADMIN`, `AWT_EMAIL`, `AWT_PASS`: read once, by migration 0009, to create the first
  superuser. Their fallbacks are well-known defaults; set them for any real deployment.
- Grafana takes `GF_*` variables (see README).

Fixed in `settings.py`: `DEBUG = False`, `ALLOWED_HOSTS = ['*']`, a hardcoded `SECRET_KEY`,
`STATIC_ROOT = static/`.

## Gotchas

- On a new database run `migrate auth` before `migrate`. Migration 0009 creates a user with the
  real `User` model but does not depend on `auth`, and Django plans `HealthChecker` (capital H
  sorts first) before `auth`, so a plain `migrate` fails on the missing `auth_user` table. The
  compose commands already do this.
- Uploaded client certificates and keys are stored under `./certificates/`.
- With `DEBUG = False`, static files come from the explicit `serve` routes in `urls.py`, reading the
  committed `static/` folder. Change `HealthChecker/static` or templates, run collectstatic, commit.
- `urls.py` uses `django.conf.urls.url`, removed in Django 4.0: moving past 3.2 needs `re_path`.
- The web container runs `manage.py runserver`, in the README's compose file too.
- `models.py`, `admin.py` and `tasks.py` each create a Redis client, so saving or deleting an
  `EnvironmentVariable` needs Redis. If Redis db 1 is flushed, re-save the variables.
- `HealthCheckRecord.request` is a curl command with the header values in it, so a token sent in a
  header ends up in the database, the admin and Grafana. Monitored calls use `verify=False`.
- The `members` group gets its permissions only when the hook first creates it; grant permissions
  for models added later by hand.
- The dashboards query `"HealthChecker_healthcheckrecord"` and `"HealthChecker_healthcheckrule"`
  directly (mixed-case names need double quotes) and use the `snuids-trafficlights-panel` plugin.
  Renaming models or fields breaks them.
- `celerybeat-schedule` and `celerybeat.pid` are committed runtime files; `--pidfile=` keeps a stale
  pid file from blocking beat. There is no `.dockerignore`, so the whole tree goes into the image.
- `DATABASES` also has a `develop` SQLite alias, but nothing routes to it.
