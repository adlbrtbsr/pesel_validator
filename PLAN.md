## Implementation Plan: PESEL Validator in a Django Application

### Scope and Goal
- **Goal**: Allow the user to enter a PESEL number, validate it against the official specification, and present the result along with the date of birth and sex.
- **Scope**: A simple Django app (1 form, 1 view, 1 template) with pure validation logic in a dedicated module and unit/integration tests.

### PESEL Validity Criteria
A PESEL number consists of 11 digits: AA BB CC D E F G H I J K

- **Length and characters**: 11 digits, only [0-9].
- **Date of birth (AA BB CC)**:
  - Structure: `YYMMDD`, where `MM` is offset by the century indicator:
    - 1800–1899: `MM + 80`
    - 1900–1999: `MM`
    - 2000–2099: `MM + 20`
    - 2100–2199: `MM + 40`
    - 2200–2299: `MM + 60`
  - After reducing month back to 1–12, the month must be valid; the day must be valid for the given month and year (including leap years per Gregorian rules).
- **Sex**: The tenth digit (index 9) indicates sex – even: female, odd: male.
- **Checksum**: Weights for the first 10 digits: [1, 3, 7, 9, 1, 3, 7, 9, 1, 3].
  - Weighted sum modulo 10: `s = (Σ(d[i] * w[i])) % 10`.
  - Control digit: `k = (10 - s) % 10`.
  - Number is valid if `k == d[10]`.

### Architecture
Minimal directory structure:

```
pesel_project/
  manage.py
  pesel_project/
    __init__.py
    settings.py
    urls.py
    wsgi.py
  validator/
    __init__.py
    apps.py
    urls.py
    views.py
    forms.py
    templates/validator/index.html
    services/pesel.py  # pure validation logic
    tests/
      __init__.py
      test_pesel_service.py
      test_form_and_view.py
```

### Request Flow (happy path)
1. User opens the home page (`/`).
2. `PESELForm` (single `CharField` with validators: required, length=11, regex=^[0-9]{11}$) accepts the number.
3. `index` view (GET/POST):
   - POST: calls `validate_pesel(pesel)` from `services/pesel.py`.
   - Receives result: `is_valid`, `birth_date` (datetime.date or None), `sex` ("F"/"M" or None), `errors` (list of messages).
   - Renders `index.html` with success/error message and details.
4. GET: renders an empty form.

### Validation Logic (services/pesel.py)
- Interface:

```python
from dataclasses import dataclass
from datetime import date

@dataclass
class PeselValidationResult:
    is_valid: bool
    birth_date: date | None
    sex: str | None   # "F" or "M"
    errors: list[str]

def validate_pesel(pesel: str) -> PeselValidationResult:
    ...
```

- Validation steps:
  1) Check: length == 11 and `pesel.isdigit()`.
  2) Extract `YY`, `MM`, `DD`; determine the century based on `MM` range and reduce month.
  3) Build `date(year, month, day)`; if ValueError → date error.
  4) Determine sex from the 10th digit: `sex = 'M' if d9 % 2 == 1 else 'F'`.
  5) Compute checksum using weights and compare with `d10`.
  6) Return result and errors list (if any).

### Form and UI
- `PESELForm`: single field, mask/placeholder "Enter 11 digits"; validators: `RegexValidator(r"^[0-9]{11}$")` and length.
- `index.html`: simple layout, validity info in a results panel:
  - When valid: green alert, show date (YYYY-MM-DD) and sex (F/M).
  - When invalid: red alert, list of errors.
- Use accessible markup, labels, and error messages.

### Routing
- `pesel_project/urls.py`: include `validator.urls` at `/`.
- `validator/urls.py`: path `""` → `views.index`, name `"index"`.

### Tests
- Unit tests in `test_pesel_service.py`:
  - Valid numbers (various centuries, sexes, edge months, leap year).
  - Errors: non-digit characters, wrong length, invalid date, wrong checksum, month out of range after reduction.
- Form/view tests in `test_form_and_view.py`:
  - GET returns 200 and contains the form.
  - POST with valid PESEL → 200 and success message + details.
  - POST with invalid PESEL → 200 and error messages.

### Quality and Security
- Server-side validations; optionally simple client-side JS (not required for correctness).
- Error handling without leaking internals (standard Django).
- XSS protection (autoescape, proper rendering of form errors).

### Local Development
1. `django-admin startproject pesel_project` (or `python -m django startproject ...`).
2. `python manage.py startapp validator`.
3. Add `validator` to `INSTALLED_APPS`.
4. Implement `services/pesel.py`, `forms.py`, `views.py`, template, and routes.
5. `python manage.py runserver` and manual checks.
6. `pytest` or `python manage.py test` – run automated tests.

### Risks and Edge Cases
- Incorrect century derivation at month boundaries (e.g., 20, 40, 60, 80).
- Feb 29 on non-leap years.
- Consistency of messages and sex labels (keep consistent in UI/tests).


