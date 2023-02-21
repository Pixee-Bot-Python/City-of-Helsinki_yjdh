from datetime import date

import pytest

from common.tests.conftest import *  # noqa
from terms.enums import TermsType
from terms.tests.factories import (
    ApplicantConsentFactory,
    ApplicantTermsApprovalFactory,
    TermsFactory,
    TermsOfServiceApprovalFactory,
)


@pytest.fixture
def applicant_consent():
    return ApplicantConsentFactory()


@pytest.fixture
def applicant_terms():
    terms = TermsFactory(
        terms_type=TermsType.APPLICANT_TERMS, effective_from=date.today()
    )
    yield terms
    terms.terms_pdf_fi.delete()
    terms.terms_pdf_en.delete()
    terms.terms_pdf_sv.delete()


@pytest.fixture
def terms_of_service():
    terms = TermsFactory(
        terms_type=TermsType.TERMS_OF_SERVICE, effective_from=date(2021, 1, 1)
    )
    yield terms

    terms.terms_pdf_fi.delete()
    terms.terms_pdf_en.delete()
    terms.terms_pdf_sv.delete()


@pytest.fixture
def applicant_terms_approval():
    return ApplicantTermsApprovalFactory()


@pytest.fixture
def terms_of_service_approval():
    return TermsOfServiceApprovalFactory()
