from rest_framework import serializers

from .models import InsurancePolicy


class InsurancePolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = InsurancePolicy
        fields = '__all__'
        read_only_fields = ["car"]
        
    def validate(self, data):
        """
        Ensure that end_date is after start_date.
        """
        start_date = data.get('start_date', None)
        end_date = data.get('end_date', None)
        
        if start_date and end_date and end_date < start_date:
            raise serializers.ValidationError("End date must be after start date.")
        
        return data