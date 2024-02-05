from django.db import models

class Sex(models.TextChoices):
    male = "M"
    female = "F"

class Age(models.TextChoices):
    RANGE_15_TO_25 = '15-25', '15-25'
    RANGE_26_TO_40 = "26-40", "26-40"
    RANGE_41_TO_55 = "41-55", "41-55" 
    RANGE_ABOVE_55 = "+55", "+55"

class User(models.Model):
    age = models.CharField(
        max_length = 5,
        choices = Age.choices,
        default = Age.RANGE_15_TO_25,
    )
    sex = models.CharField(
        max_length = 1,
        choices = Sex.choices,
        default = Sex.male,
    )
    predicted_face = models.CharField(
        max_length = 20,
        default = "Brad Pitt",
    )

    def __str__(self) -> str:
        return f"{self.age} - {self.sex}"
    
    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

