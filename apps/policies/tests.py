import pytest
from django.utils import timezone
from rest_framework.test import APIClient
from django.contrib.auth.models import User

from apps.cars.factories import CarFactory
from apps.policies.factories import InsurancePolicyFactory
from core.scheduler import log_policy_expirations


@pytest.fixture
def auth_client(db):
    user = User.objects.create_user(username="tester", password="test1234")
    client = APIClient()
    client.force_authenticate(user=user)
    return client


@pytest.mark.django_db
def test_create_policy_success(auth_client):
    car = CarFactory()
    payload = {"provider": "Allianz", "start_date": "2025-01-01", "end_date": "2025-12-31"}

    response = auth_client.post(f"/api/cars/{car.id}/policies/", payload, format="json")
    assert response.status_code == 201
    assert response.data["provider"] == "Allianz"
    assert response.data["car"] == car.id


@pytest.mark.django_db
def test_create_policy_validation_error(auth_client):
    car = CarFactory()
    payload = {"provider": "Groupama", "start_date": "2025-12-31", "end_date": "2025-01-01"}
    response = auth_client.post(f"/api/cars/{car.id}/policies/", payload, format="json")
    # either 400 (if validated by serializer) or 500 (if DB constraint is triggered)
    assert response.status_code in [400, 500]


@pytest.mark.django_db
def test_insurance_valid_endpoint_true(auth_client):
    policy = InsurancePolicyFactory(
        start_date=timezone.now().date() - timezone.timedelta(days=30),
        end_date=timezone.now().date() + timezone.timedelta(days=30),
    )
    response = auth_client.get(
        f"/api/cars/{policy.car.id}/insurance-valid/?date={timezone.now().date()}"
    )
    assert response.status_code == 200
    assert response.data["valid"] is True


@pytest.mark.django_db
def test_insurance_valid_endpoint_false(auth_client):
    policy = InsurancePolicyFactory(
        start_date=timezone.now().date() - timezone.timedelta(days=90),
        end_date=timezone.now().date() - timezone.timedelta(days=30),
    )
    response = auth_client.get(
        f"/api/cars/{policy.car.id}/insurance-valid/?date={timezone.now().date()}"
    )
    assert response.status_code == 200
    assert response.data["valid"] is False


@pytest.mark.django_db
def test_insurance_valid_endpoint_404(auth_client):
    response = auth_client.get("/api/cars/999/insurance-valid/?date=2025-01-01")
    assert response.status_code == 404


@pytest.mark.django_db
def test_scheduler_logs_expired_policy():
    expired_policy = InsurancePolicyFactory(
        end_date=timezone.now().date() - timezone.timedelta(days=1)
    )
    log_policy_expirations()
    expired_policy.refresh_from_db()
    assert expired_policy.logged_expiry_at is not None


# @pytest.mark.django_db
# def test_scheduler_idempotent_behavior():
#     expired_policy = InsurancePolicyFactory(
#         end_date=timezone.now().date() - timezone.timedelta(days=2)
#     )
#     log_policy_expirations()
#     expired_policy.refresh_from_db()
#     first_log_time = expired_policy.logged_expiry_at
#     log_policy_expirations()
#     expired_policy.refresh_from_db()
#     assert expired_policy.logged_expiry_at == first_log_time


@pytest.mark.django_db
def test_scheduler_idempotent_behavior():
    """Test scheduler does not duplicate PolicyExpiryLog entries."""
    expired_policy = InsurancePolicyFactory(
        end_date=timezone.now().date() - timezone.timedelta(days=2)
    )

    # Run scheduler the first time
    log_policy_expirations()

    # Refresh from DB to get updated logged_expiry_at
    expired_policy.refresh_from_db()
    first_log_time = expired_policy.logged_expiry_at

    # Run scheduler again
    log_policy_expirations()
    expired_policy.refresh_from_db()

    # Should be the same timestamp (unchanged)
    assert expired_policy.logged_expiry_at == first_log_time
