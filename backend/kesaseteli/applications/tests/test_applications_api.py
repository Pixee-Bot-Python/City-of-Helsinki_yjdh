import pytest
from django.test import override_settings
from rest_framework.reverse import reverse
from shared.audit_log.models import AuditLogEntry

from applications.api.v1.serializers import (
    ApplicationSerializer,
    SummerVoucherSerializer,
)
from applications.enums import ApplicationStatus
from applications.models import Application
from common.tests.factories import ApplicationFactory, SummerVoucherFactory


def get_detail_url(application):
    return reverse("v1:application-detail", kwargs={"pk": application.id})


@pytest.mark.django_db
def test_applications_list(api_client, company):
    response = api_client.get(reverse("v1:application-list"))

    assert response.status_code == 200


@pytest.mark.django_db
def test_application_single_read(api_client, application):
    response = api_client.get(get_detail_url(application))

    assert response.status_code == 200


@pytest.mark.django_db
def test_application_put(api_client, application):
    data = ApplicationSerializer(application).data
    data["invoicer_name"] = "test"
    response = api_client.put(
        get_detail_url(application),
        data,
    )

    assert response.status_code == 200
    assert response.data["invoicer_name"] == "test"


@pytest.mark.django_db
def test_application_patch(api_client, company):
    application = ApplicationFactory(company=company, status=ApplicationStatus.DRAFT)
    data = {"status": ApplicationStatus.SUBMITTED.value}
    response = api_client.patch(
        get_detail_url(application),
        data,
    )

    assert response.status_code == 200
    assert response.data["status"] == ApplicationStatus.SUBMITTED

    application.refresh_from_db()
    assert application.status == ApplicationStatus.SUBMITTED


@pytest.mark.django_db
def test_add_summer_voucher(api_client, application, summer_voucher):
    original_summer_voucher_count = application.summer_vouchers.count()

    data = ApplicationSerializer(application).data

    summer_voucher_data = SummerVoucherSerializer(summer_voucher).data
    summer_voucher_data.pop("id")
    data["summer_vouchers"].append(summer_voucher_data)

    response = api_client.put(
        get_detail_url(application),
        data,
    )

    assert response.status_code == 200
    assert (
        response.data["summer_vouchers"][-1]["ordering"]
        == original_summer_voucher_count
    )  # Index starts from 0

    application.refresh_from_db()
    summer_voucher_count_after_update = application.summer_vouchers.count()
    assert summer_voucher_count_after_update == original_summer_voucher_count + 1


@pytest.mark.django_db
def test_update_summer_voucher(api_client, application, summer_voucher):
    data = ApplicationSerializer(application).data
    data["summer_vouchers"][0]["summer_voucher_id"] = "test"

    response = api_client.put(
        get_detail_url(application),
        data,
    )

    assert response.status_code == 200
    assert response.data["summer_vouchers"][0]["summer_voucher_id"] == "test"


@pytest.mark.django_db
def test_remove_single_summer_voucher(api_client, application, summer_voucher):
    original_summer_voucher_count = application.summer_vouchers.count()

    data = ApplicationSerializer(application).data
    data["summer_vouchers"].pop()

    response = api_client.put(
        get_detail_url(application),
        data,
    )

    assert response.status_code == 200

    application.refresh_from_db()
    summer_voucher_count_after_update = application.summer_vouchers.count()
    assert summer_voucher_count_after_update == original_summer_voucher_count - 1


@pytest.mark.django_db
def test_remove_all_summer_vouchers(api_client, application):
    SummerVoucherFactory.create_batch(size=3, application=application)
    data = ApplicationSerializer(application).data
    data.pop("summer_vouchers")
    response = api_client.put(
        get_detail_url(application),
        data,
    )

    assert response.status_code == 200
    assert response.data["summer_vouchers"] == []

    application.refresh_from_db()
    assert application.summer_vouchers.count() == 0


@pytest.mark.django_db
def test_application_create(api_client, company):
    response = api_client.post(
        reverse("v1:application-list"),
        {},
    )

    assert response.status_code == 201
    assert Application.objects.count() == 1
    assert response.data["company"]["name"] == company.name
    assert response.data["company"]["business_id"] == company.business_id

    for field in [
        field
        for field in Application._meta.fields
        if field.name not in ["created_at", "modified_at"]
    ]:
        assert field.name in response.data


@pytest.mark.django_db
@override_settings(MOCK_FLAG=True)
def test_application_create_mock(api_client, company):
    response = api_client.post(
        reverse("v1:application-list"),
        {},
    )

    assert response.status_code == 201
    for field in [
        field
        for field in Application._meta.fields
        if field.name not in ["created_at", "modified_at"]
    ]:
        assert field.name in response.data


@pytest.mark.django_db
def test_application_delete_not_allowed(api_client, application):
    response = api_client.delete(get_detail_url(application))

    assert response.status_code == 405


@pytest.mark.django_db
@override_settings(
    AUDIT_LOG_ORIGIN="TEST_SERVICE",
)
def test_application_create_writes_audit_log(api_client, user_with_profile, company):
    response = api_client.post(
        reverse("v1:application-list"),
        {},
    )

    assert response.status_code == 201

    audit_event = AuditLogEntry.objects.first().message["audit_event"]
    assert audit_event["actor"] == {
        "ip_address": "127.0.0.1",
        "role": "USER",
        "user_id": str(user_with_profile.pk),
        "provider": "",
    }
    assert audit_event["operation"] == "CREATE"
    assert audit_event["target"] == {
        "id": response.data["id"],
        "type": "Application",
    }
    assert audit_event["status"] == "SUCCESS"


@pytest.mark.django_db
@override_settings(
    AUDIT_LOG_ORIGIN="TEST_SERVICE",
)
def test_application_update_writes_audit_log(
    api_client, user_with_profile, application
):
    application.invoicer_name = "test1"
    application.save()

    data = ApplicationSerializer(application).data
    data["invoicer_name"] = "test2"
    response = api_client.put(
        get_detail_url(application),
        data,
    )

    assert response.status_code == 200
    assert response.data["invoicer_name"] == "test2"

    audit_event = AuditLogEntry.objects.first().message["audit_event"]
    assert audit_event["actor"] == {
        "ip_address": "127.0.0.1",
        "role": "USER",
        "user_id": str(user_with_profile.pk),
        "provider": "",
    }
    assert audit_event["operation"] == "UPDATE"
    assert audit_event["target"] == {
        "id": response.data["id"],
        "type": "Application",
        "changes": ["invoicer_name changed from test1 to test2"],
    }
    assert audit_event["status"] == "SUCCESS"


@pytest.mark.django_db
@override_settings(
    AUDIT_LOG_ORIGIN="TEST_SERVICE",
)
def test_application_create_writes_audit_log_if_not_authenticated(
    unauthenticated_api_client,
):
    response = unauthenticated_api_client.post(
        reverse("v1:application-list"),
        {},
    )

    assert response.status_code == 403

    audit_event = AuditLogEntry.objects.first().message["audit_event"]
    assert audit_event["actor"] == {
        "ip_address": "127.0.0.1",
        "role": "ANONYMOUS",
        "user_id": "",
        "provider": "",
    }
    assert audit_event["operation"] == "CREATE"
    assert audit_event["target"]["type"] == "Application"
    assert audit_event["status"] == "FORBIDDEN"


@pytest.mark.django_db
def test_application_create_double(api_client, company):
    response = api_client.post(
        reverse("v1:application-list"),
        {},
    )

    assert response.status_code == 201

    response = api_client.post(
        reverse("v1:application-list"),
        {},
    )

    assert response.status_code == 400
    assert str(response.data[0]) == "Company can have only one draft application"


@pytest.mark.django_db
def test_applications_list_only_finds_own_application(api_client, application):
    ApplicationFactory()

    assert Application.objects.count() == 2

    response = api_client.get(reverse("v1:application-list"))

    assert response.status_code == 200
    assert len(response.data) == 1
    assert str(response.data[0]["id"]) == str(application.id)
