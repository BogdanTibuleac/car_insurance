from datetime import datetime
from itertools import chain
from operator import itemgetter

from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from apps.cars.models import Car
from apps.cars.serializers import CarSerializer
from apps.claims.models import Claim
from apps.claims.serializers import ClaimSerializer
from apps.policies.models import InsurancePolicy
from apps.policies.serializers import InsurancePolicySerializer

# ===============================================================
# 🧠 SERVICE LAYER
# ===============================================================

class CarService:
    """Business logic for cars, policies, and claims."""

    @staticmethod
    def create_policy(car, data):
        serializer = InsurancePolicySerializer(data=data)
        serializer.is_valid(raise_exception=True)
        policy = serializer.save(car=car)
        return policy, serializer.data

    @staticmethod
    def create_claim(car, data):
        serializer = ClaimSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        claim = serializer.save(car=car)
        return claim, serializer.data

    @staticmethod
    def check_insurance_validity(car, date_str):
        if not date_str:
            raise ValidationError({"detail": "Missing required query parameter: date"})

        try:
            date_obj = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            raise ValidationError({"detail": "Invalid date format. Expected YYYY-MM-DD."})

        if not (1900 <= date_obj.year <= 2100):
            raise ValidationError({"detail": "Date out of valid range (1900–2100)."})

        valid = InsurancePolicy.objects.filter(
            car=car, start_date__lte=date_obj, end_date__gte=date_obj
        ).exists()

        return {"carId": car.id, "date": date_str, "valid": valid}

    @staticmethod
    def get_car_history(car):
        policies = InsurancePolicy.objects.filter(car=car).values(
            "id", "start_date", "end_date", "provider"
        )
        claims = Claim.objects.filter(car=car).values(
            "id", "claim_date", "amount", "description"
        )

        policies_list = [
            {
                "type": "POLICY",
                "policyId": p["id"],
                "startDate": p["start_date"],
                "endDate": p["end_date"],
                "provider": p["provider"],
                "date_key": p["start_date"],
            }
            for p in policies
        ]

        claims_list = [
            {
                "type": "CLAIM",
                "claimId": c["id"],
                "claimDate": c["claim_date"],
                "amount": float(c["amount"]),
                "description": c["description"],
                "date_key": c["claim_date"],
            }
            for c in claims
        ]

        combined = sorted(chain(policies_list, claims_list), key=itemgetter("date_key"))
        for entry in combined:
            entry.pop("date_key", None)
        return combined


# ===============================================================
# 🎯 CONTROLLER LAYER (DRF VIEWSET)
# ===============================================================
class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    def perform_create(self, serializer):
        """
        Automatically assign the logged-in user as the owner when creating a car.
        """
        serializer.save(owner=self.request.user)

    @action(detail=True, methods=["post"], url_path="policies")
    def create_policy(self, request, pk=None):
        """POST /api/cars/{carId}/policies"""
        car = get_object_or_404(Car, pk=pk)
        policy, data = CarService.create_policy(car, request.data)
        headers = {"Location": f"/api/cars/{car.id}/policies/{policy.id}"}
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["post"], url_path="claims")
    def create_claim(self, request, pk=None):
        """POST /api/cars/{carId}/claims"""
        car = get_object_or_404(Car, pk=pk)
        claim, data = CarService.create_claim(car, request.data)
        headers = {"Location": f"/api/cars/{car.id}/claims/{claim.id}"}
        return Response(data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["get"], url_path="insurance-valid")
    def insurance_valid(self, request, pk=None):
        """GET /api/cars/{carId}/insurance-valid?date=YYYY-MM-DD"""
        car = get_object_or_404(Car, pk=pk)
        result = CarService.check_insurance_validity(car, request.query_params.get("date"))
        return Response(result, status=status.HTTP_200_OK)

    @action(detail=True, methods=["get"], url_path="history")
    def get_history(self, request, pk=None):
        """GET /api/cars/{carId}/history"""
        car = get_object_or_404(Car, pk=pk)
        history = CarService.get_car_history(car)
        return Response(history, status=status.HTTP_200_OK)
