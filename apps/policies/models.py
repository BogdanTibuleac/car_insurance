from django.db import models
from apps.cars.models import Car
from django.utils import timezone

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
    
class InsuranceExpiryLog(models.Model):
    policy = models.OneToOneField("InsurancePolicy", on_delete = models.CASCADE, related_name = "expiry_log")
    logged_at = models.DateTimeField(default = timezone.now)
    
    class Meta:
        db_table = 'insurance_expiry_log'
        indexes = [models.Index(fields=["policy", "logged_at"], name="idx_expirylog_policy_loggedat")]
        constraints = [models.UniqueConstraint(fields=["policy"], name="uniq_expirylog_policy")] #each policy can have only one expiry log entry in the database
        
    def __str__(self):
        return f"Expiry log for Policy #{self.policy.id} logged at {self.logged_at}"