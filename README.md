## PESEL Validator (Django)

A minimal Django application that validates Polish PESEL numbers, decodes date of birth and sex, and shows validation results via a simple form. The core validation logic lives in a pure Python service for easy unit testing.

### Features
- Validate PESEL format (11 digits)
- Decode birth date with correct century offsets
- Determine sex from the tenth digit (even = F, odd = M)
- Verify checksum using official weights
- Unit tests for the service and basic integration tests for the form/view

### Tech Stack
- Python 3.12
- Django 5.2
- Pytest + pytest-django
- Optional: Docker, Makefile

---

### Quickstart (local)
Prerequisites: Python 3.12+, pip. Optional: make.

```bash
# (optional) create and activate a virtualenv
python -m venv .venv
source .venv/bin/activate

# install dependencies
pip install -r requirements.txt

# run DB migrations (SQLite by default)
python manage.py migrate

# start the dev server
python manage.py runserver 0.0.0.0:8000
```

Open `http://localhost:8000` and enter a PESEL to validate.

If you prefer Makefile targets:
```bash
make install
make migrate
make run
```

---

### Running tests
```bash
pytest -q
# or via Makefile
make test
```

---

### Docker
Build and run with Docker:
```bash
make docker-build
make docker-run
# or directly
docker build -t pesel-validator:latest .
docker run --rm -p 8000:8000 --env-file .env pesel-validator:latest
```

The container exposes port 8000 and runs:
```bash
python manage.py runserver 0.0.0.0:8000
```

---

### Environment configuration
Environment variables are loaded from a `.env` file at the project root (via `python-dotenv`). Useful keys:

- `DJANGO_DEBUG` (default: `true`)
- `DJANGO_SECRET_KEY` (required when `DJANGO_DEBUG=false`)
- `DJANGO_ALLOWED_HOSTS` (comma-separated; default: `*` in debug)
- `DJANGO_CSRF_TRUSTED_ORIGINS` (comma-separated)
- `DB_ENGINE` (default: `django.db.backends.sqlite3`)
- `DB_NAME` (default: `db.sqlite3` path when using SQLite)
- `DB_USER`, `DB_PASSWORD`, `DB_HOST`, `DB_PORT` (for non-SQLite engines)
- `LANGUAGE_CODE` (default: `en-us`), `TIME_ZONE` (default: `UTC`)
- `USE_I18N`, `USE_TZ`

Example `.env` (development):
```env
DJANGO_DEBUG=true
DJANGO_ALLOWED_HOSTS=*
# DJANGO_SECRET_KEY=change-me-for-prod
# DB_ENGINE=django.db.backends.sqlite3
# DB_NAME=db.sqlite3
```

---

### Project structure
```text
pesel_validator/
  manage.py
  pesel_project/
    settings.py
    urls.py
    env_utils.py
    wsgi.py
  validator/
    forms.py
    views.py
    urls.py
    services/
      pesel.py
    templates/
      validator/
        index.html
    tests/
      test_pesel_service.py
      test_form_and_view.py
  requirements.txt
  Makefile
  Dockerfile
  db.sqlite3 (created automatically in dev)
```

Key endpoints:
- `/` — home page with the PESEL form
- `/admin/` — Django admin (no custom models in this project)

---

### PESEL validation overview
A PESEL consists of 11 digits: `AA BB CC D E F G H I J K`.

- Length and characters: must be 11 digits (`0-9`).
- Date of birth (`YYMMDD`): the month encodes century by adding an offset:
  - 1800–1899: `MM + 80`
  - 1900–1999: `MM`
  - 2000–2099: `MM + 20`
  - 2100–2199: `MM + 40`
  - 2200–2299: `MM + 60`
  After removing the offset, the date must be valid (leap years included).
- Sex: the 10th digit (index 9) — even → `F`, odd → `M`.
- Checksum: weights for first 10 digits are `[1,3,7,9,1,3,7,9,1,3]`.
  Let `s = (Σ(d[i] * w[i])) % 10`. Control digit `k = (10 - s) % 10` must equal digit 11.

The core validator is implemented in `validator/services/pesel.py` and returns a result object with `is_valid`, `birth_date`, `sex`, and `errors`.

---

### Makefile targets
- `install`: install Python dependencies
- `run`: start Django dev server on `0.0.0.0:8000`
- `migrate`: run Django migrations
- `makemigrations`: generate migrations
- `test`: run the test suite (`pytest -q`)
- `docker-build`: build the Docker image `pesel-validator:latest`
- `docker-run`: run the image mapping `8000:8000` and using `.env`
- `docker-stop`: stop running containers created from that image
