from rest_framework import serializers
from apps.accounts.serializers import AccountSerializer
from .models import Car


class CarSerializer(serializers.ModelSerializer):
    owner = AccountSerializer(read_only=True)  # nested owner representation

    class Meta:
        model = Car
        fields = "__all__"
