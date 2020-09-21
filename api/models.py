from __future__ import unicode_literals

from django.contrib.auth.base_user import AbstractBaseUser
from django.contrib.auth.models import PermissionsMixin, UserManager
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.utils.translation import ugettext_lazy as _
from django.utils import timezone
from django.db import models
  

class Config(models.Model):
    host = models.CharField(max_length=100,  blank=True)
    porta = models.CharField(max_length=100,  blank=True)
    automacao = models.CharField(max_length=100,  blank=True)
    ativo = models.BooleanField(default=False)
    data_licensa = models.CharField(max_length=300,  blank=True)
    tempo_cmd = models.CharField(max_length=100,  blank=True)
    start_auto = models.BooleanField(default=False)
    automacao_ativo = models.BooleanField(default=False)
    emulado = models.BooleanField(default=False)
    usuario = models.CharField(max_length=100,  blank=True)
    host_app = models.CharField(max_length=100,  blank=True)
    porta_app = models.CharField(max_length=100,  blank=True)
    pks =  models.BooleanField(default=False)

    def __str__(self):
        return self.host

    class meta:
        verbose_name_plural = 'Config'

class User(AbstractBaseUser, PermissionsMixin):
    """
    An abstract base class implementing a fully featured User model with
    admin-compliant permissions.

    Username and password are required. Other fields are optional.
    """
    username_validator = UnicodeUsernameValidator()

    username = models.CharField(
        _('username'),
        max_length=150,
        unique=True,
        help_text=_(
            'Required. 150 characters or fewer. Letters, digits and @/./+/-/_ only.'),
        validators=[username_validator],
        error_messages={
            'unique': _("A user with that username already exists."),
        },
    )
    password = models.CharField(_('password'), max_length=128)
    last_login = models.DateTimeField(_('last login'), blank=True, null=True)
    first_name = models.CharField(_('first name'), max_length=30, blank=True)
    last_name = models.CharField(_('last name'), max_length=150, blank=True)
    email = models.EmailField(_('email address'), blank=True)
    nivel = models.IntegerField(_('nivel'),default=0, blank=True)
    is_staff = models.BooleanField(
        _('staff status'),
        default=False,
        help_text=_(
            'Designates whether the user can log into this admin site.'),
    )
    is_active = models.BooleanField(
        _('active'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    is_superuser = models.BooleanField(
        _('superuser'),
        default=True,
        help_text=_(
            'Designates whether this user should be treated as active. '
            'Unselect this instead of deleting accounts.'
        ),
    )
    date_joined = models.DateTimeField(_('date joined'), default=timezone.now)

    objects = UserManager()

    EMAIL_FIELD = 'email'
    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email']

    class Meta:
        verbose_name = _('user')
        verbose_name_plural = _('users')
