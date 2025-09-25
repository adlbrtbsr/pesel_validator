import pytest
from django.urls import reverse


def test_get_index(client):
    resp = client.get('/')
    assert resp.status_code == 200
    assert b'PESEL' in resp.content


def test_post_valid(client):
    resp = client.post('/', data={'pesel': '90051212318'})
    assert resp.status_code == 200
    assert b'Valid PESEL' in resp.content


def test_post_invalid(client):
    resp = client.post('/', data={'pesel': '123'})
    assert resp.status_code == 200
    assert b'Invalid PESEL' in resp.content or b'Enter exactly 11 digits' in resp.content
