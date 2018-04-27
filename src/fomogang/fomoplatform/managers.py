from django.contrib.auth.base_user import BaseUserManager


class UserManager(BaseUserManager):
    use_in_migrations = True

    def _create_user(self, id, **extra_fields):
        if not id:
            raise ValueError("id must be provided")

        user = self.model(id=id, **extra_fields)
        user.save(using=self._db)
        return user

    def create_user(self, id, **extra_fields):
        return self._create_user(id, **extra_fields)