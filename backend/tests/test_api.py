from datetime import timedelta
from unittest.mock import patch

import pytest
from django.contrib.auth.models import User
from django.db import OperationalError
from django.test import Client
from django.utils import timezone

from pension.models import Goal

pytestmark = pytest.mark.django_db


@pytest.fixture
def user():
    return User.objects.create_user(username="owner", password="test-password-strong")


@pytest.fixture
def client(user):
    client = Client(enforce_csrf_checks=True)
    client.get("/api/auth/session")
    response = client.post(
        "/api/auth/login",
        {"username": "owner", "password": "test-password-strong"},
        content_type="application/json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )
    assert response.status_code == 200
    return client


def payload(**changes):
    data = {
        "monthly_income": "30000.00",
        "money_basis": "today",
        "payout_start": timezone.now().date().replace(day=1).isoformat(),
        "payout_months": 120,
        "initial_capital": "0.00",
        "monthly_contribution": "8000.00",
        "risk_notes": "Риск требует уточнения",
    }
    return data | changes


def post(client, url, data):
    return client.post(
        url,
        data,
        content_type="application/json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )


def test_auth_and_csrf_boundaries(user):
    anonymous = Client(enforce_csrf_checks=True)
    assert anonymous.get("/api/v1/goals").status_code == 401
    assert (
        anonymous.post(
            "/api/auth/login",
            {"username": "owner", "password": "test-password-strong"},
            content_type="application/json",
        ).status_code
        == 403
    )
    assert anonymous.get("/api/auth/session").json() == {"user": None}
    assert (
        post(anonymous, "/api/auth/login", {"username": "owner", "password": "wrong"}).status_code
        == 401
    )


def test_save_reload_confirm_is_idempotent(client, user):
    response = post(client, "/api/v1/goals", payload())
    assert response.status_code == 201, response.content
    goal = response.json()
    assert goal["confirmed_at"] is None
    assert goal["monthly_income"] == "30000.00"
    assert "owner" not in goal
    assert Goal.objects.get(id=goal["id"]).owner == user
    assert client.get("/api/v1/goals").json()["items"][0] == goal
    url = f"/api/v1/goals/{goal['id']}/confirm"
    first = post(client, url, {"confirmed": True})
    assert first.status_code == 200
    assert first.json()["confirmed_at"] is not None
    assert post(client, url, {"confirmed": True}).json() == first.json()
    assert Goal.objects.count() == 1
    assert client.get("/api/v1/goals")["Cache-Control"] == "no-store, private"


def test_session_mutations_require_csrf_and_reject_foreign_origin(client):
    assert (
        client.post("/api/v1/goals", payload(), content_type="application/json").status_code == 403
    )
    assert client.post("/api/auth/logout", content_type="application/json").status_code == 403
    response = client.post(
        "/api/v1/goals",
        payload(),
        content_type="application/json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
        HTTP_ORIGIN="https://attacker.invalid",
    )
    assert response.status_code == 403
    assert Goal.objects.count() == 0


def test_no_cross_user_read_or_confirmation(client):
    other = User.objects.create_user(username="other")
    goal = Goal.objects.create(owner=other, **payload())
    assert client.get("/api/v1/goals").json()["items"] == []
    assert post(client, f"/api/v1/goals/{goal.id}/confirm", {"confirmed": True}).status_code == 404
    goal.refresh_from_db()
    assert goal.confirmed_at is None


@pytest.mark.parametrize(
    "changes",
    [
        {"initial_capital": "-1"},
        {"monthly_income": "0"},
        {"monthly_contribution": "1.001"},
        {"initial_capital": 10},
        {"monthly_income": "NaN"},
        {"payout_months": True},
        {"payout_months": 0},
        {"payout_months": 1201},
        {"money_basis": "invented"},
        {"risk_notes": "   "},
        {"owner_id": 1},
        {"confirmed_at": "2030-01-01"},
        {"payout_start": "2000-01-01"},
        {"payout_start": "2090-02-02"},
    ],
)
def test_input_validation(client, changes):
    response = post(client, "/api/v1/goals", payload(**changes))
    assert response.status_code == 422, response.content
    assert Goal.objects.count() == 0


@pytest.mark.parametrize("confirmation", [False, 1, "true"])
def test_confirmation_must_be_explicit_and_not_expired(client, user, confirmation):
    goal = Goal.objects.create(owner=user, **payload())
    assert (
        post(client, f"/api/v1/goals/{goal.id}/confirm", {"confirmed": confirmation}).status_code
        == 422
    )
    goal.payout_start = timezone.now().date().replace(day=1) - timedelta(days=1)
    goal.save()
    assert post(client, f"/api/v1/goals/{goal.id}/confirm", {"confirmed": True}).status_code == 409


def test_logout_revokes_session(client):
    assert post(client, "/api/auth/logout", {}).status_code == 200
    assert client.get("/api/v1/goals").status_code == 401


def test_login_lockout_after_five_failures(user):
    client = Client(enforce_csrf_checks=True)
    client.get("/api/auth/session")
    responses = [
        post(client, "/api/auth/login", {"username": "owner", "password": "wrong"})
        for _ in range(5)
    ]
    assert responses[-1].status_code == 429
    assert (
        post(
            client, "/api/auth/login", {"username": "owner", "password": "test-password-strong"}
        ).status_code
        == 429
    )


@pytest.mark.parametrize("body", ["[]", "null", '{"username":3,"password":4}', "{"])
def test_malformed_login_never_crashes(body):
    client = Client(enforce_csrf_checks=True)
    client.get("/api/auth/session")
    response = client.post(
        "/api/auth/login",
        body,
        content_type="application/json",
        HTTP_X_CSRFTOKEN=client.cookies["csrftoken"].value,
    )
    assert response.status_code == 400


def test_health_and_readiness():
    client = Client()
    assert client.get("/health/live").status_code == 200
    assert client.get("/health/ready").status_code == 200
    with patch("pension.health.connection.cursor", side_effect=OperationalError("private info")):
        response = client.get("/health/ready")
    assert response.status_code == 503
    assert "private info" not in response.content.decode()


def test_list_is_bounded_and_offset_validated(client, user):
    Goal.objects.bulk_create([Goal(owner=user, **payload()) for _ in range(51)])
    first = client.get("/api/v1/goals").json()
    assert len(first["items"]) == 50
    assert first["has_more"] is True
    assert len(client.get("/api/v1/goals?offset=50").json()["items"]) == 1
    assert client.get("/api/v1/goals?offset=-1").status_code == 422
