# Register your models here.
# apps/cars/admin.py
from django.contrib import admin

from .models import Car


@admin.register(Car)
class CarAdmin(admin.ModelAdmin):
    list_display = ("id", "vin", "make", "model", "year_of_manufacture", "owner", "created_at")
    search_fields = ("vin", "make", "model", "owner__username")
