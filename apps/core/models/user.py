import uuid

from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.hashers import check_password, make_password
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.core.exceptions import ValidationError
from django.db import models


def _normalize_email(email: str) -> str:
    return BaseUserManager.normalize_email(email) if email else email


class CustomUserManager(BaseUserManager):
    use_in_migrations = True

    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('El email es obligatorio')
        email = _normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)

        if not extra_fields['is_staff'] or not extra_fields['is_superuser']:
            raise ValueError('Superuser debe tener is_staff e is_superuser en True')

        return self.create_user(email, password, **extra_fields)


class CustomUser(AbstractBaseUser, PermissionsMixin):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=64, blank=True)
    last_name = models.CharField(max_length=64, blank=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    is_platform_staff = models.BooleanField(default=False)
    pin_hash = models.CharField(max_length=128, blank=True, help_text='Hash del PIN de 4 dígitos')
    pin_enabled = models.BooleanField(default=False)
    date_joined = models.DateTimeField(auto_now_add=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    objects = CustomUserManager()

    def __str__(self):
        return self.email

    @property
    def tenant(self):
        membership = getattr(self, 'membership', None)
        return membership.tenant if membership else None

    @property
    def role(self):
        membership = getattr(self, 'membership', None)
        return membership.role if membership else None

    def set_pin(self, raw_pin: str):
        if raw_pin is None or raw_pin == '':
            self.pin_hash = ''
            self.pin_enabled = False
            return
        if not raw_pin.isdigit() or len(raw_pin) != 4:
            raise ValidationError('El PIN debe tener exactamente 4 dígitos numéricos.')
        self.pin_hash = make_password(raw_pin)
        self.pin_enabled = True

    def check_pin(self, raw_pin: str) -> bool:
        if not self.pin_enabled or not self.pin_hash:
            return False
        return check_password(raw_pin, self.pin_hash)

    def disable_pin(self):
        self.pin_hash = ''
        self.pin_enabled = False

    def get_short_name(self) -> str:
        if self.first_name:
            return self.first_name
        return self.email.split('@')[0]
