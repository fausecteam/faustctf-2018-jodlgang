from django.db import models
from django.contrib.auth.models import AbstractUser
from .managers import UserManager


class User(AbstractUser):
    id = models.IntegerField('id', unique=True, primary_key=True)
    email = models.EmailField('email address', blank=True)
    name = models.CharField('name', max_length=100, blank=True)

    objects = UserManager()

    USERNAME_FIELD = 'id'
    REQUIRED_FIELDS = []

    class Meta:
        verbose_name = 'user'
        verbose_name_plural = 'users'

    def get_name(self):
        return self.name

    def __str__(self):
        return "{:d} {}".format(self.id, self.name)