from os.path import splitext

from django.contrib.auth.models import AbstractUser
from django.db import models
from django_lifecycle import hook, LifecycleModelMixin, BEFORE_SAVE, BEFORE_UPDATE

from theme.helper import make_thumb, uuid_name_upload_to


class User(AbstractUser):
    pass

    class Meta:
        ordering = ["-date_joined"]


class Profile(LifecycleModelMixin, models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
    )
    avatar = models.ImageField(upload_to=uuid_name_upload_to)

    @hook(BEFORE_SAVE, when="avatar", has_changed=True)
    def on_image_change(self):
        if self.avatar:
            image_width = self.avatar.width
            image_extension = splitext(self.avatar.name)[-1].lower()

            if image_width > 1024 or image_extension not in (".jpg", ".jpeg"):
                thumb_file = make_thumb(self.avatar.file, 1024, 1024, 80)
                self.avatar.save(thumb_file.name, thumb_file, save=False)
