from django.db import models
from imagekit.models import ProcessedImageField
from pilkit.processors import ResizeToFill

from theme.utils import uuid_name_upload_to


class TimeStampedModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        abstract = True


class Brand(TimeStampedModel):
    logo_thumb = ProcessedImageField(
        upload_to=uuid_name_upload_to,
        processors=[ResizeToFill(82, 82)],
        format="JPEG",
        options={"quality": 100},
    )
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


# class BrandThumbnail(TimeStampedModel):
#     brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
#     thumb = ProcessedImageField(
#         upload_to=uuid_name_upload_to,
#         processors=[ResizeToFill(512, 512)],
#         format="JPEG",
#         options={"quality": 100},
#     )


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)

    def __str__(self):
        return self.name


class Product(TimeStampedModel):
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    thumb = ProcessedImageField(
        upload_to=uuid_name_upload_to,
        processors=[ResizeToFill(512, 512)],
        format="JPEG",
        options={"quality": 100},
    )
    name = models.CharField(max_length=100, unique=True)
    price = models.IntegerField()
    sale_price = models.IntegerField()

    def __str__(self):
        return self.name
