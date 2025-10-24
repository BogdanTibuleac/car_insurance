import datetime

from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models


class Car(models.Model):
    vin = models.CharField(max_length=17, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year_of_manufacture = models.PositiveIntegerField(
        validators=[MinValueValidator(1900),
                    MaxValueValidator(datetime.date.today().year +1)]
    )
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cars')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'car'
        indexes = [models.Index(fields=["vin"], name="idx_car_vin")]
        constraints = [models.UniqueConstraint(fields=["vin"], name="uq_car_vin")]

    def __str__(self):
        return f"{self.make} {self.model} ({self.year_of_manufacture})"
