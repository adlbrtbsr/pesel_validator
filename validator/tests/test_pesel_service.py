import pytest
from datetime import date
from validator.services.pesel import validate_pesel


def test_valid_1900s_female():
    # 1990-05-12, female, checksum matches
    pesel = '90051200009'
    res = validate_pesel(pesel)
    assert res.is_valid
    assert res.birth_date == date(1990, 5, 12)
    assert res.sex == 'F'


def test_valid_2000s_male():
    # 2003-12-31 -> month 12 + 20 = 32; using plausible checksum (example PESEL)
    pesel = '03323100013'
    res = validate_pesel(pesel)
    assert res.is_valid
    assert res.birth_date == date(2003, 12, 31)
    assert res.sex == 'M'


def test_invalid_characters():
    res = validate_pesel('12345abc901')
    assert not res.is_valid
    assert any('11 digits' in e for e in res.errors)


def test_wrong_length():
    res = validate_pesel('1234567890')
    assert not res.is_valid
    assert any('11 digits' in e for e in res.errors)


def test_invalid_date():
    # 1999-02-30 is invalid
    res = validate_pesel('99023012319')
    assert not res.is_valid
    assert any('birth date' in e for e in res.errors)


def test_invalid_month_encoding():
    # month 13 is invalid encoding
    res = validate_pesel('99133112318')
    assert not res.is_valid
    assert any('month encoding' in e for e in res.errors)


def test_invalid_checksum():
    # Alter last digit to break checksum
    good = '90051212318'
    bad = good[:-1] + ('0' if good[-1] != '0' else '1')
    res = validate_pesel(bad)
    assert not res.is_valid
    assert any('checksum' in e for e in res.errors)
