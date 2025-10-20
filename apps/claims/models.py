from django.db import models
from apps.cars.models import Car

class Claim(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name="claims")
    claim_date = models.DateField()
    description = models.TextField()
    amount = models.DecimalField(max_digits=10, decimal_places=2)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "claim"
        indexes = [models.Index(fields=["car", "claim_date"], name="idx_claim_car_date")]

    def __str__(self):
        return f"Claim #{self.id} for {self.car} - {self.claim_date}"
