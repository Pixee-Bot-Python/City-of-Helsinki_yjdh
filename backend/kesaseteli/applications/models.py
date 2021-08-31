from django.db import models
from django.utils.translation import gettext_lazy as _
from encrypted_fields.fields import EncryptedCharField
from shared.models.abstract_models import HistoricalModel, TimeStampedModel, UUIDModel

from applications.enums import (
    ApplicationStatus,
    ATTACHMENT_CONTENT_TYPE_CHOICES,
    AttachmentType,
)
from companies.models import Company


class Application(HistoricalModel, TimeStampedModel, UUIDModel):
    company = models.ForeignKey(
        Company,
        on_delete=models.CASCADE,
        related_name="applications",
        verbose_name=_("company"),
    )
    status = models.CharField(
        max_length=64,
        verbose_name=_("status"),
        choices=ApplicationStatus.choices,
        default=ApplicationStatus.DRAFT,
    )
    street_address = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_("invoicer work address"),
    )

    # contact information
    contact_person_name = models.CharField(
        blank=True,
        max_length=256,
        verbose_name=_("contact person name"),
    )
    contact_person_email = models.EmailField(
        blank=True, verbose_name=_("contact person email")
    )
    contact_person_phone_number = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_("contact person phone number"),
    )

    # invoicer information
    is_separate_invoicer = models.BooleanField(
        default=False,
        verbose_name=_("is separate invoicer"),
        help_text=_("invoicing is not handled by the contact person"),
    )
    invoicer_name = models.CharField(
        blank=True,
        max_length=256,
        verbose_name=_("invoicer name"),
    )
    invoicer_email = models.EmailField(blank=True, verbose_name=_("invoicer email"))
    invoicer_phone_number = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_("invoicer phone number"),
    )

    class Meta:
        verbose_name = _("application")
        verbose_name_plural = _("applications")
        ordering = ["-created_at"]


class SummerVoucher(HistoricalModel, TimeStampedModel, UUIDModel):
    application = models.ForeignKey(
        Application,
        on_delete=models.CASCADE,
        related_name="summer_vouchers",
        verbose_name=_("application"),
    )
    summer_voucher_id = models.CharField(
        max_length=256, blank=True, verbose_name=_("summer voucher id")
    )
    contact_name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_("contact name"),
    )
    contact_email = models.EmailField(
        blank=True,
        verbose_name=_("contact email"),
    )
    work_postcode = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_("work postcode"),
    )

    employee_name = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_("employee name"),
    )
    employee_school = models.CharField(
        max_length=256,
        blank=True,
        verbose_name=_("employee school"),
    )
    employee_ssn = EncryptedCharField(
        max_length=32,
        blank=True,
        verbose_name=_("employee social security number"),
    )
    employee_phone_number = models.CharField(
        max_length=64,
        blank=True,
        verbose_name=_("employee phone number"),
    )

    is_unnumbered_summer_voucher = models.BooleanField(
        default=False,
        verbose_name=_("is unnumbered summer voucher"),
    )
    unnumbered_summer_voucher_reason = models.TextField(
        default="",
        verbose_name=_("unnumbered summer voucher reason"),
    )
    ordering = models.IntegerField(default=0)

    class Meta:
        verbose_name = _("summer voucher")
        verbose_name_plural = _("summer vouchers")
        ordering = ["-application__created_at", "ordering"]


class Attachment(UUIDModel, TimeStampedModel):
    """
    created_at field from TimeStampedModel provides the upload timestamp
    """

    summer_voucher = models.ForeignKey(
        SummerVoucher,
        verbose_name=_("summer voucher"),
        related_name="attachments",
        on_delete=models.CASCADE,
    )
    attachment_type = models.CharField(
        max_length=64,
        verbose_name=_("attachment type in business rules"),
        choices=AttachmentType.choices,
    )
    content_type = models.CharField(
        max_length=100,
        choices=ATTACHMENT_CONTENT_TYPE_CHOICES,
        verbose_name=_("technical content type of the attachment"),
    )
    attachment_file = models.FileField(verbose_name=_("application attachment content"))

    class Meta:
        verbose_name = _("attachment")
        verbose_name_plural = _("attachments")
        ordering = ["-summer_voucher__created_at", "attachment_type", "-created_at"]
