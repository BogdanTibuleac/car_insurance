from datetime import datetime
from itertools import chain
from operator import itemgetter

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404

from .models import Car
from .serializers import CarSerializer
from apps.policies.models import InsurancePolicy
from apps.policies.serializers import InsurancePolicySerializer
from apps.claims.models import Claim
from apps.claims.serializers import ClaimSerializer


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    # --- Create Insurance Policy ---
    @action(detail=True, methods=["post"], url_path="policies")
    def create_policy(self, request, pk=None):
        """
        POST /api/cars/{carId}/policies
        Creates a new insurance policy for the given car.
        """
        car = get_object_or_404(Car, pk=pk)
        serializer = InsurancePolicySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        policy = serializer.save(car=car)
        location = f"/api/cars/{car.id}/policies/{policy.id}"
        headers = {"Location": location}

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # --- Create Insurance Claim ---
    @action(detail=True, methods=["post"], url_path="claims")
    def create_claim(self, request, pk=None):
        """
        POST /api/cars/{carId}/claims
        Creates a new claim for the given car.
        """
        car = get_object_or_404(Car, pk=pk)
        serializer = ClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        claim = serializer.save(car=car)
        location = f"/api/cars/{car.id}/claims/{claim.id}"
        headers = {"Location": location}

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    # --- Check Insurance Validity ---
    @action(detail=True, methods=["get"], url_path="insurance-valid")
    def insurance_valid(self, request, pk=None):
        car = get_object_or_404(Car, pk=pk)
        date_str = request.query_params.get("date")

        if not date_str:
            return Response({"detail": "Missing required query parameter: date"}, status=400)

        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response({"detail": "Invalid date format. Expected YYYY-MM-DD."}, status=400)

        if not (1900 <= d.year <= 2100):
            return Response({"detail": "Date out of valid range (1900–2100)."}, status=400)

        valid = InsurancePolicy.objects.filter(
            car=car,
            start_date__lte=d,
            end_date__gte=d
        ).exists()

        return Response({"carId": car.id, "date": date_str, "valid": valid}, status=200)

    # --- Car History ---
    @action(detail=True, methods=["get"], url_path="history")
    def get_history(self, request, pk=None):
        """
        GET /api/cars/{carId}/history
        Returns a combined chronological list of policies and claims.
        """
        car = get_object_or_404(Car, pk=pk)

        policies = InsurancePolicy.objects.filter(car=car).values(
            "id", "start_date", "end_date", "provider"
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

        claims = Claim.objects.filter(car=car).values(
            "id", "claim_date", "amount", "description"
        )
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

        return Response(combined, status=200)
