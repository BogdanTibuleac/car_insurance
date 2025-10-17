from django.db import models

class Car(models.Model):
    vin = models.CharField(max_length=17, unique=True)
    make = models.CharField(max_length=50)
    model = models.CharField(max_length=50)
    year_of_manufacture = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'cars'

    def __str__(self):
        return f"{self.make} {self.model} ({self.year_of_manufacture})"
