from os.path import splitext

from django.db import models
from django_lifecycle import LifecycleModelMixin, BEFORE_SAVE, hook

from theme.utils import make_thumb, uuid_name_upload_to


class Product(LifecycleModelMixin, models.Model):
    brand = models.CharField(max_length=100)  # TODO: 나중에 Brand Model ForeignKey 변환
    category = models.CharField(
        max_length=100
    )  # TODO: 나중에 Category Model ForeignKey 변환
    thumb = models.ImageField(upload_to=uuid_name_upload_to)
    name = models.CharField(max_length=100, unique=True)
    price = models.IntegerField()
    sale_price = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-pk"]

    def __str__(self):
        return f"{self.brand} - {self.brand} - {self.thumb} - {self.name} - {self.price} - {self.sale_price} - {self.created_at}"

    @hook(BEFORE_SAVE, when="thumb", has_changed=True)
    def on_image_change(self):
        if self.thumb:
            image_width = self.thumb.width
            image_extension = splitext(self.thumb.name)[-1].lower()

            if image_width > 1024 or image_extension not in (".jpg", ".jpeg"):
                thumb_file = make_thumb(self.thumb.file, 512, 512, 100)
                self.thumb.save(thumb_file.name, thumb_file, save=False)
