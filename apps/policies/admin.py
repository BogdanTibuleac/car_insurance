from django.contrib import admin
from .models import InsurancePolicy
# Register your models here.

@admin.register(InsurancePolicy)
class InsurancePolicyAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "provider", "start_date", "end_date", "logged_expiry_at")
    list_filter = ("provider", "start_date", "end_date")
    search_fields = ("car__vin", "provider")