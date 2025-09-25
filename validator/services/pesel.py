from dataclasses import dataclass
from datetime import date
from typing import Optional, List


@dataclass
class PeselValidationResult:
    is_valid: bool
    birth_date: Optional[date]
    sex: Optional[str]  # "F" or "M"
    errors: List[str]


def _decode_year_month(yy: int, mm: int) -> tuple[Optional[int], Optional[int]]:
    """Return (year, month) with proper century or (None, None) if invalid month encoding."""
    if 1 <= mm <= 12:
        return 1900 + yy, mm
    if 21 <= mm <= 32:
        return 2000 + yy, mm - 20
    if 41 <= mm <= 52:
        return 2100 + yy, mm - 40
    if 61 <= mm <= 72:
        return 2200 + yy, mm - 60
    if 81 <= mm <= 92:
        return 1800 + yy, mm - 80
    return None, None


def validate_pesel(pesel: str) -> PeselValidationResult:
    errors: List[str] = []

    if len(pesel) != 11 or not pesel.isdigit():
        errors.append("PESEL must be 11 digits")
        return PeselValidationResult(False, None, None, errors)

    digits = [int(ch) for ch in pesel]

    yy = digits[0] * 10 + digits[1]
    mm = digits[2] * 10 + digits[3]
    dd = digits[4] * 10 + digits[5]

    year, month = _decode_year_month(yy, mm)
    if year is None or month is None:
        errors.append("Invalid month encoding in PESEL")
        return PeselValidationResult(False, None, None, errors)

    try:
        birth_date = date(year, month, dd)
    except ValueError:
        errors.append("Invalid birth date in PESEL")
        birth_date = None

    sex = 'M' if digits[9] % 2 == 1 else 'F'

    weights = [1, 3, 7, 9, 1, 3, 7, 9, 1, 3]
    s = sum(d * w for d, w in zip(digits[:10], weights)) % 10
    control = (10 - s) % 10
    if control != digits[10]:
        errors.append("Invalid checksum")

    is_valid = len(errors) == 0
    if not is_valid and birth_date is not None and any('birth date' in e for e in errors):
        birth_date = None

    return PeselValidationResult(is_valid, birth_date, sex if is_valid else None, errors)
