from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    pass

    class Meta:
        ordering = ["-date_joined"]
