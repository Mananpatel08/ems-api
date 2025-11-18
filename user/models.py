from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.exceptions import ValidationError
from django.utils import timezone
from services.models import BaseCoreModel
from django.db import models
from django.db.models import BooleanField, ImageField, Index
from .enums import UserRoleEnum


def validate_file_size(value):
    max_size = 5 * 1024 * 1024
    if value.size > max_size:
        raise ValidationError("image size must be less than 5MB")


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("The Email field must be set")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)
        extra_fields.setdefault("user_role", UserRoleEnum.SUPER_ADMIN.value)

        if not extra_fields.get("is_staff"):
            raise ValueError("Superuser must have is_staff=True.")
        if not extra_fields.get("is_superuser"):
            raise ValueError("Superuser must have is_superuser=True.")
        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin, BaseCoreModel):
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=50, blank=True)
    last_name = models.CharField(max_length=50, blank=True)
    phone_number = models.CharField(max_length=15, blank=True)
    profile_photo = ImageField(
        upload_to="user_profile",
        validators=[validate_file_size],
        blank=True,
        default="user_profile/user-icon.png",
    )
    date_joined = models.DateTimeField(default=timezone.now)
    user_role = models.CharField(
        max_length=20,
        choices=UserRoleEnum.choices(),
        default=UserRoleEnum.USER.value,
    )

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = BooleanField(default=False)

    objects = CustomUserManager()
    USERNAME_FIELD = "email"

    class Meta:
        db_table = "users"
        verbose_name = "User"
        verbose_name_plural = "Users"
        indexes = [
            Index(fields=["email"]),
        ]
        ordering = BaseCoreModel.Meta.ordering

    def __str__(self):
        return self.email
