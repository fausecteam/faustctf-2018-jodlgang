from django.db import models
from django.contrib.auth.models import AbstractBaseUser
from .managers import UserManager


class User(AbstractBaseUser):
    id = models.AutoField('id', primary_key=True, blank=False)
    email = models.EmailField('email address', blank=False, unique=True, null=False)
    name = models.CharField('name', max_length=100, blank=True)
    is_staff = models.BooleanField('staff', default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_name(self):
        return self.name

    def __str__(self):
        return self.email

    def get_full_name(self):
        if len(self.name) > 0:
            return self.name
        return self.email

    def get_short_name(self):
        if len(self.name) > 0:
            return self.name
        return self.email

    # this method is required to login super user from admin panel
    def has_perm(self, perm, obj=None):
        return self.is_staff

    # this method is required to login super user from admin panel
    def has_module_perms(self, app_label):
        return self.is_staff
