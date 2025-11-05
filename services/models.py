from uuid import uuid4

from django.db.models import (
    BooleanField,
    CharField,
    DateTimeField,
    ForeignKey,
    Manager,
    Model,
    PositiveSmallIntegerField,
    QuerySet,
    SET_NULL,
    TextField,
    UUIDField,
)
from django.utils.timezone import now
from django.utils.translation import gettext_lazy as _


class BaseCoreModel(Model):
    id = UUIDField(default=uuid4, primary_key=True, editable=False, verbose_name=_("Id"))
    created_at = DateTimeField(auto_now_add=True, verbose_name="Created At")

    objects = Manager()

    class Meta:
        abstract = True
        ordering = [
            "-created_at",
        ]


class SoftDeletionQuerySet(QuerySet):
    def delete(self, soft=True):
        if soft:
            return self.update(deleted_at=now())
        else:
            return super().delete()


class SoftDeletionManager(Manager):
    def get_queryset(self):
        return SoftDeletionQuerySet(self.model, using=self._db).filter(deleted_at__isnull=True)


class SoftDeleteModel(BaseCoreModel):
    """To soft delete records"""

    deleted_at = DateTimeField(verbose_name="Deleted At", null=True, blank=True)

    all_objects = Manager()
    objects = SoftDeletionManager()

    class Meta(BaseCoreModel.Meta):
        abstract = True

    def delete(self, using=None, soft=True, *args, **kwargs):
        if soft:
            # Soft delete the current instance
            self.deleted_at = now()
            self.save(using=using)

        else:
            # Perform hard delete if soft deletion is not enabled
            return super().delete(*args, **kwargs, using=using)


class TimeAuditModel(BaseCoreModel):
    """To path when the record was created and last modified"""

    updated_at = DateTimeField(auto_now=True, verbose_name="Last Modified At")

    class Meta(BaseCoreModel.Meta):
        abstract = True


class UserAuditModel(TimeAuditModel):
    """To path when the record was created and last modified"""

    created_by = ForeignKey(
        "user.CustomUser",
        on_delete=SET_NULL,
        related_name="%(class)s_created_by",
        verbose_name="Created By",
        null=True,
        blank=True,
    )
    updated_by = ForeignKey(
        "user.CustomUser",
        on_delete=SET_NULL,
        related_name="%(class)s_updated_by",
        verbose_name="Last Modified By",
        null=True,
        blank=True,
    )

    class Meta(BaseCoreModel.Meta):
        abstract = True


class BaseAuditModel(UserAuditModel, SoftDeleteModel):
    """To path when the record was created and last modified"""

    class Meta(BaseCoreModel.Meta):
        abstract = True


class AbstractAddress(BaseAuditModel):
    address_line_1 = TextField(verbose_name=_("Address line 1"), blank=True)
    postcode = CharField(max_length=8, blank=True, verbose_name=_("Postcode"))
    month_at_address = PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Month at address"))
    year_at_address = PositiveSmallIntegerField(null=True, blank=True, verbose_name=_("Year at address"))
    is_current_address = BooleanField(default=True)

    class Meta(BaseAuditModel.Meta):
        abstract = True

    ordering = ["is_current_address", "-created_at"]

    def __str__(self):
        return f"{self.address_line_1} <{self.postcode}-{self.is_current_address}>"
