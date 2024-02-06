from datetime import datetime
from typing import List

from django.conf import settings
from django.urls import reverse

from applications.enums import AttachmentType
from applications.models import Application, Attachment
from common.utils import hash_file
from users.models import User

MANNER_OF_RECEIPT = "sähköinen asiointi"


def _prepare_top_level_dict(application: Application, case_records: List[dict]) -> dict:
    """Prepare the dictionary that is sent to Ahjo"""
    application_date = application.created_at.isoformat()
    message_title = f"Avustukset työnantajille, Työllisyyspalvelut, \
Työnantajan Helsinki-lisä, Työnantaja {application.company_name} {application.company.business_id},\
hakemusnumero {application.application_number}"

    handler = application.calculation.handler
    case_dict = {
        "Title": message_title,
        "Acquired": application_date,
        "ClassificationCode": "02 05 01 00",
        "ClassificationTitle": "Kunnan myöntämät avustukset",
        "Language": "fi",
        "PublicityClass": "Julkinen",
        "InternalTitle": message_title,
        "Subjects": [
            {"Subject": "Helsinki-lisät", "Scheme": "hki-yhpa"},
            {"Subject": "kunnan myöntämät avustukset", "Scheme": "hki-yhpa"},
            {"Subject": "työnantajat", "Scheme": "hki-yhpa"},
            {"Subject": "työllisyydenhoito"},
        ],
        "PersonalData": "Sisältää erityisiä henkilötietoja",
        "Reference": f"{application.application_number}",
        "Records": case_records,
        "Agents": [
            {
                "Role": "sender_initiator",
                "CorporateName": application.company.name,
                "ContactPerson": application.contact_person,
                "Type": "ExterOnal",
                "Email": application.company_contact_person_email,
                "AddressStreet": application.company.street_address,
                "AddressPostalCode": application.company.postcode,
                "AddressCity": application.company.city,
            },
            {
                "Role": "draftsman",
                "Name": f"{handler.last_name}, {handler.first_name}",
                "ID": handler.ad_username,
            },
        ],
    }
    return case_dict


def _prepare_record_document_dict(attachment: Attachment) -> dict:
    """Prepare a documents dict for a record"""
    # If were running in mock mode, use the local file URI
    file_url = reverse("ahjo_attachment_url", kwargs={"uuid": attachment.id})
    hash_value = hash_file(attachment.attachment_file)
    attachment.ahjo_hash_value = hash_value
    attachment.save()
    return {
        "FileName": f"{attachment.attachment_file.name}",
        "FormatName": f"{attachment.content_type}",
        "HashAlgorithm": "sha256",
        "HashValue": hash_value,
        "FileURI": f"{settings.API_BASE_URL}{file_url}",
    }


def _prepare_record(
    record_title: str,
    record_type: str,
    acquired: datetime,
    documents: List[dict],
    handler: User,
    publicity_class: str = "Salassa pidettävä",
):
    """Prepare a single record dict for Ahjo."""

    record_dict = {
        "Title": record_title,
        "Type": record_type,
        "Acquired": acquired,
        "PublicityClass": publicity_class,
        "SecurityReasons": ["JulkL (621/1999) 24.1 § 25 k"],
        "Language": "fi",
        "PersonalData": "Sisältää erityisiä henkilötietoja",
    }

    if record_title == "Hakemus":
        record_dict["MannerOfReceipt"] = MANNER_OF_RECEIPT

    record_dict["Documents"] = documents
    record_dict["Agents"] = [
        {
            "Role": "mainCreator",
            "Name": f"{handler.last_name}, {handler.first_name}",
            "ID": handler.ad_username,
        }
    ]

    return record_dict


def _prepare_case_records(
    application: Application, pdf_summary: Attachment
) -> List[dict]:
    """Prepare the list of case records from  application's attachments,
    including the pdf summary of the application."""
    case_records = []
    handler = application.calculation.handler
    main_document_record = _prepare_record(
        "Hakemus",
        "hakemus",
        application.created_at.isoformat(),
        [_prepare_record_document_dict(pdf_summary)],
        handler,
    )

    case_records.append(main_document_record)

    for attachment in application.attachments.exclude(
        attachment_type=AttachmentType.PDF_SUMMARY
    ):
        document_record = _prepare_record(
            "Hakemuksen Liite",
            "liite",
            attachment.created_at.isoformat(),
            [_prepare_record_document_dict(attachment)],
            handler,
        )
        case_records.append(document_record)

    return case_records


def prepare_open_case_payload(
    application: Application, pdf_summary: Attachment
) -> dict:
    "Prepare the complete dictionary payload that is sent to Ahjo"
    case_records = _prepare_case_records(application, pdf_summary)
    payload = _prepare_top_level_dict(application, case_records)
    return payload
