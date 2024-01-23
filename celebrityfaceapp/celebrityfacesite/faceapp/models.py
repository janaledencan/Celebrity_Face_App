from django.db import models

class Sex(models.TextChoices):
    male = "M"
    female = "F"


class User(models.Model):
    age = models.PositiveIntegerField()
    sex = models.CharField(
        max_length = 1,
        choices = Sex.choices,
        default = Sex.male,
    )

    def __str__(self) -> str:
        return f"{self.age} - {self.sex}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

