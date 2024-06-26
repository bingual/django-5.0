# Generated by Django 5.0.5 on 2024-05-07 14:37

import django_lifecycle.mixins
import theme.utils
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="Product",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("brand", models.CharField(max_length=100)),
                ("category", models.CharField(max_length=100)),
                ("thumb", models.ImageField(upload_to=theme.utils.uuid_name_upload_to)),
                ("name", models.CharField(max_length=100, unique=True)),
                ("price", models.IntegerField()),
                ("sale_price", models.IntegerField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
            ],
            options={
                "ordering": ["-pk"],
            },
            bases=(django_lifecycle.mixins.LifecycleModelMixin, models.Model),
        ),
    ]
