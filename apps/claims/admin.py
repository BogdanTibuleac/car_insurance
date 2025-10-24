from django.contrib import admin

from .models import Claim


@admin.register(Claim)
class ClaimAdmin(admin.ModelAdmin):
    list_display = ("id", "car", "claim_date", "description", "amount", "created_at")
    search_fields = ("car", "claim_date",)
