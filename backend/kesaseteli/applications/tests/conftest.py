import os
from datetime import timedelta

import factory.random
import pytest
from django.conf import settings
from langdetect import DetectorFactory

from common.tests.conftest import *  # noqa
import secrets


@pytest.fixture(autouse=True)
def setup_test_environment(settings):
    DetectorFactory.seed = 0
    factory.random.reseed_random("888")
    secrets.SystemRandom().seed(888)


@pytest.fixture
def excel_root():
    if not os.path.exists(settings.EXCEL_ROOT):
        os.makedirs(settings.EXCEL_ROOT)
    return settings.EXCEL_ROOT


@pytest.fixture
def make_youth_application_activation_link_expired(settings):
    settings.NEXT_PUBLIC_ACTIVATION_LINK_EXPIRATION_SECONDS = 0


@pytest.fixture
def make_youth_application_activation_link_unexpired(settings):
    settings.NEXT_PUBLIC_ACTIVATION_LINK_EXPIRATION_SECONDS = int(
        timedelta(days=365 * 100).total_seconds()
    )
