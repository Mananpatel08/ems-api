from datetime import datetime
from services.models import BaseAuditModel
from django.db.models import (
    BigIntegerField,
    BooleanField,
    CASCADE,
    CharField,
    DateField,
    ForeignKey,
    IntegerChoices,
    JSONField,
    Max,
    OneToOneField,
    SET_NULL,
    TextChoices,
)
from django.db.models.fields import DateTimeField, PositiveSmallIntegerField
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.functions import Cast, Substr
from django.utils.translation import gettext_lazy as _


def generate_form_number():
    today = datetime.now()
    date_str = today.strftime("%Y%d%m")  # YYYYDDMM
    prefix = f"FN-{date_str}"
    prefix_length = len(prefix)

    max_seq_data = (
        RootForm.all_objects.filter(form_number__startswith=prefix)
        .annotate(
            numeric_part=Cast(
                Substr("form_number", prefix_length + 2), BigIntegerField()
            )
        )
        .aggregate(max_seq=Max("numeric_part"))
    )

    if max_seq_data["max_seq"] is not None:
        next_seq = max_seq_data["max_seq"] + 1
    else:
        next_seq = 1

    return f"{prefix}-{next_seq}"


class FormStep(IntegerChoices):
    STARTED = 0, _("Not completed any stpe")
    PERSONAL_DETAILS = 1, _("Personal Details")
    SERVICE_DETAILS = 2, _("Service Details")


class RootForm(BaseAuditModel):
    class Status(TextChoices):
        PENDING = "pending", _("Pending")
        IN_PROGRESS = "in_progress", _("In progress")
        COMPLETED = "completed", _("Completed")

    step_completed = JSONField(default=list)
    status = CharField(
        verbose_name=_("Status"),
        choices=Status.choices,
        default=Status.PENDING,
        max_length=12,
    )
    user = ForeignKey(
        "user.CustomUser",
        on_delete=SET_NULL,
        null=True,
        blank=True,
        related_name="root_form",
    )
    completed_at = DateTimeField(null=True, blank=True, verbose_name=_("Completed at"))
    current_step = PositiveSmallIntegerField(
        default=0, verbose_name=_("Current step"), choices=FormStep.choices
    )
    form_number = CharField(
        verbose_name=_("Application number"),
        unique=True,
        max_length=30,
        default=generate_form_number,
    )

    class Meta(BaseAuditModel.Meta):
        verbose_name = _("Root Form")
        verbose_name_plural = _("Root Forms")
        db_table = "root_form"
        ordering = ["-created_at"]

    def __str__(self):
        return f"Form {self.form_number}"


class PersonalDetails(BaseAuditModel):
    class Gender(TextChoices):
        MALE = "male", _("Male")
        FEMALE = "female", _("Female")
        OTHER = "other", _("Other")

    root_form = OneToOneField(
        "form.RootForm", on_delete=CASCADE, related_name="personal_details"
    )
    email = CharField(max_length=100, verbose_name=_("Email"))
    first_name = CharField(max_length=50, verbose_name=_("First name"))
    middle_name = CharField(max_length=50, verbose_name=_("Middle name"))
    last_name = CharField(max_length=50, verbose_name=_("Last name"))
    gender = CharField(max_length=6, verbose_name=_("Gender"), choices=Gender.choices)
    mobile_number = CharField(max_length=15, verbose_name=_("Mobile number"))
    pan_number = CharField(max_length=10, verbose_name=_("PAN number"))
    voter_id = CharField(
        max_length=16, verbose_name=_("Voter ID"), null=True, blank=True
    )
    is_step_completed = BooleanField(default=False, verbose_name=_("Is step completed"))

    class Meta(BaseAuditModel.Meta):
        verbose_name = _("Personal Details")
        verbose_name_plural = _("Personal Details")
        db_table = "personal_details"
        ordering = ["-created_at"]


class ServiceDetails(BaseAuditModel):
    class Post_Choices(TextChoices):
        REVENUE_CLERK = "revenue_clerk", _("Revenue Clerk")
        REVENUE_TALATI = "revenue_talati", _("Revenue Talati")
        DEPUTY_MAMLATDAR = "deputy_mamlatdar", _("Deputy Mamlatdar")

    root_form = OneToOneField(
        "form.RootForm", on_delete=CASCADE, related_name="service_details"
    )
    joining_appointment_date = DateField()
    regular_appointment_date = DateField(null=True, blank=True)
    post_at_appointment = CharField(
        max_length=50,
        choices=Post_Choices.choices,
        verbose_name=_("Post at appointment"),
    )
    ppan = CharField(
        max_length=20,
        verbose_name="Permanent Pension Account Number (PPAN)",
        null=True,
        blank=True,
    )
    pran = CharField(
        max_length=20,
        verbose_name="Permanent Retirement Account Number (PRAN)",
        null=True,
        blank=True,
    )
    is_step_completed = BooleanField(default=False, verbose_name=_("Is step completed"))

    class Meta(BaseAuditModel.Meta):
        verbose_name = _("Service Details")
        verbose_name_plural = _("Service Details")
        db_table = "service_details"
        ordering = ["-created_at"]


class ExamDetail(BaseAuditModel):
    EXAM_TYPES = [
        ("pre_service", "Pre Service Exam"),
        ("ccc", "CCC Exam"),
        ("ccc_plus", "CCC Plus Exam"),
        ("lrq", "LRQ Exam"),
        ("hrq", "HRQ Exam"),
    ]

    service_details = ForeignKey(
        ServiceDetails, on_delete=CASCADE, related_name="exams"
    )
    exam_type = CharField(max_length=20, choices=EXAM_TYPES)
    passing_date = DateField(null=True, blank=True)
    attempt_count = PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)], null=True, blank=True
    )

    def __str__(self):
        return f"{self.get_exam_type_display()} - {self.service_details.id}"


STEP_MODEL_MAPPING = {
    "PersonalDetails": FormStep.PERSONAL_DETAILS,
    "ServiceDetails": FormStep.SERVICE_DETAILS,
}
