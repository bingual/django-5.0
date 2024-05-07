from typing import List

from django.core.files import File
from django.db import models
from django.urls import reverse
from django_lifecycle import LifecycleModelMixin
from taggit.managers import TaggableManager

from accounts.models import User
from theme.utils import uuid_name_upload_to


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Note(LifecycleModelMixin, TimeStampedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=100)
    content = models.TextField()
    tags = TaggableManager(blank=True, help_text="쉼표로 구분하여 작성해주세요.")

    class Meta:
        ordering = ["-pk"]

    def get_absolute_url(self) -> str:
        return reverse("photolog:note_detail", kwargs={"pk": self.pk})


class Photo(TimeStampedModel):
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    image = models.ImageField(upload_to=uuid_name_upload_to)

    @classmethod
    def create_photos(cls, note: Note, photo_file_list: List[File]) -> List["Photo"]:
        if not note.pk:
            raise ValueError("Note를 먼저 저장해주세요.")

        photo_list = []
        for photo_file in photo_file_list:
            photo = cls(note=note)
            photo.image.save(photo_file.name, photo_file, save=False)
            photo_list.append(photo)

        cls.objects.bulk_create(photo_list)

        return photo_list


class Comment(TimeStampedModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    note = models.ForeignKey(Note, on_delete=models.CASCADE)
    message = models.TextField()

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return self.message
