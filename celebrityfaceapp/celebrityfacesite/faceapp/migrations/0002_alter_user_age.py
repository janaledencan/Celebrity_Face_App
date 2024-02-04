# Generated by Django 4.2 on 2024-02-04 16:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("faceapp", "0001_initial"),
    ]

    operations = [
        migrations.AlterField(
            model_name="user",
            name="age",
            field=models.CharField(
                choices=[
                    ("15-25", "First Group"),
                    ("26-40", "Second Group"),
                    ("41-55", "Third Group"),
                    ("+55", "Fourth Group"),
                ],
                default="15-25",
                max_length=5,
            ),
        ),
    ]
