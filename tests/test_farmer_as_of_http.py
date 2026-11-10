"""Season-date behavior exercised through the actual HTTP route."""

from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from govisense.api.auth import create_access_token
from govisense.api.main import app
from govisense.data.crop_requirements import get_crop_requirements


@pytest.fixture
def client():
    token = create_access_token({"sub": "farmer_kamal", "role": "farmer"})
    with TestClient(app, headers={"Authorization": f"Bearer {token}"}) as http:
        yield http


@pytest.mark.parametrize("as_of", ["2026-02-30", "2026-13-01", "not-a-date"])
def test_invalid_date_is_422(client, as_of):
    assert client.get('/api/farmer/top3', params={"as_of": as_of}).status_code == 422


@pytest.mark.parametrize("month", [0, 13, -1])
def test_invalid_month_is_422(client, month):
    assert client.get('/api/farmer/top3', params={"current_month": month}).status_code == 422


@pytest.mark.parametrize("reference", ["2026-06-15", "2026-11-10", "2026-01-15"])
def test_date_drives_season_filter_and_is_echoed(client, reference):
    response = client.get('/api/farmer/top3', params={"as_of": reference})
    assert response.status_code == 200
    body = response.json()
    month = int(reference[5:7])
    assert body['as_of'] == reference
    assert body['planting_month'] == month
    assert datetime.fromisoformat(body['generated_at']).tzinfo is not None
    requirements = get_crop_requirements()
    for crop in body['top3']:
        assert requirements[crop['crop_id']].season_fits(month)
    if month == 1:
        assert body['top3'] == []
    if month == 11:
        assert {crop['crop_id'] for crop in body['top3']} == {'brinjal', 'tomato'}
        for crop in body['top3']:
            assert crop['price_forecast'] is None
            assert crop['expected_net_profit_per_acre'] is None
            assert crop['spi_ratio_at_harvest'] is None


def test_default_uses_today(client):
    before = datetime.now(timezone.utc).date().isoformat()
    response = client.get('/api/farmer/top3')
    after = datetime.now(timezone.utc).date().isoformat()
    assert response.status_code == 200
    assert response.json()['as_of'] in (before, after)
    assert response.json()['planting_month'] == int(response.json()['as_of'][5:7])


def test_conflicting_month_rejected(client):
    response = client.get('/api/farmer/top3', params={"as_of": "2026-06-15", "current_month": 11})
    assert response.status_code == 422
    assert response.json()['detail']['reason_code'] == 'AS_OF_MONTH_CONFLICT'


def test_conflicting_month_aliases_rejected(client):
    response = client.get('/api/farmer/top3', params={"planting_month": 6, "current_month": 11})
    assert response.status_code == 422
    assert response.json()['detail']['reason_code'] == 'AS_OF_MONTH_CONFLICT'
