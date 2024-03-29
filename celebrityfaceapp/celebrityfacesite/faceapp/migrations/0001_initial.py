# Generated by Django 4.2 on 2024-01-23 21:54

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="User",
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
                ("age", models.PositiveIntegerField()),
                (
                    "sex",
                    models.CharField(
                        choices=[("M", "Male"), ("F", "Female")],
                        default="M",
                        max_length=1,
                    ),
                ),
            ],
        ),
    ]
