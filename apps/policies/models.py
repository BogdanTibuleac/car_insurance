from django.db import models
from apps.cars.models import Car

# Create your models here.
class InsurancePolicy(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE, related_name='policies')
    provider = models.CharField(max_length=100, blank = True, null = True)
    start_date = models.DateField()
    end_date = models.DateField()
    
    logged_expiry_at = models.DateTimeField(blank = True, null = True)
    
    class Meta:
        db_table = 'insurance_policy'
        indexes = [models.Index(fields=["car", "start_date", "end_date"], name="idx_policy_car_dates")]
        constraints = [models.CheckConstraint(check=models.Q(end_date__gte=models.F('start_date')), name='chk_policy_end_after_start')]
        
    def __str__(self):
        return f"Policy #{self.id} for car {self.car.id} ({self.start_date} to {self.end_date})"