from os.path import splitext
from uuid import uuid4

from PIL import Image
from django.core.files import File
from django.core.files.base import ContentFile
from django.db import models
from django.utils import timezone
from django.utils.encoding import force_str


def uuid_name_upload_to(instance: models.Model, filename: str) -> str:
    app_label = instance.__class__._meta.app_label
    cls_name = instance.__class__.__name__.lower()
    ymd_path = force_str(timezone.now().strftime("%Y/%m/%d"))
    extension = splitext(filename)[-1].lower()
    new_filename = uuid4().hex + extension
    return "/".join((app_label, cls_name, ymd_path, new_filename))


def make_thumb(
    image_file: File, max_width: int = 1024, max_height: int = 1024, quality=80
) -> File:
    pil_image = Image.open(image_file)
    max_size = (max_width, max_height)
    pil_image.thumbnail(max_size)
    if pil_image.mode == "RGBA":
        pil_image = pil_image.convert("RGB")

    thumb_name = splitext(image_file.name)[0] + ".jpg"
    thumb_file = ContentFile(b"", name=thumb_name)
    pil_image.save(thumb_file, format="jpeg", quality=quality)

    return thumb_file
