from datetime import datetime
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from itertools import chain
from operator import itemgetter 

from .models import Car
from .serializers import CarSerializer
from apps.policies.serializers import InsurancePolicySerializer
from apps.policies.models import InsurancePolicy
from apps.claims.serializers import ClaimSerializer
from apps.claims.models import Claim


class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all()
    serializer_class = CarSerializer

    # ---  create policy ---
    @action(detail=True, methods=["post"], url_path="policies")
    def create_policy(self, request, pk=None):
        car = self.get_object()
        serializer = InsurancePolicySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save(car=car)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    # ---  check insurance validity ---
    @action(detail=True, methods=["get"], url_path="insurance-valid")
    def insurance_valid(self, request, pk=None):
        # 1. Retrieve car or return 404
        car = get_object_or_404(Car, pk=pk)

        # 2. Extract and validate date parameter
        date_str = request.query_params.get("date")
        if not date_str:
            return Response(
                {"detail": "Missing required query parameter: date"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            d = datetime.strptime(date_str, "%Y-%m-%d").date()
        except ValueError:
            return Response(
                {"detail": "Invalid date format. Expected YYYY-MM-DD."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if d.year < 1900 or d.year > 2100:
            return Response(
                {"detail": "Date out of valid range (1900–2100)."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 3. Check if any policy covers this date
        valid = InsurancePolicy.objects.filter(
            car=car,
            start_date__lte=d,
            end_date__gte=d
        ).exists()

        # 4. Return response
        return Response(
            {
                "carId": car.id,
                "date": date_str,
                "valid": valid
            },
            status=status.HTTP_200_OK
        )

    @action(detail=True, methods=["post"], url_path="claims")
    def create_claim(self, request, pk=None):
        car = get_object_or_404(Car, pk=pk)
        serializer = ClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        claim = serializer.save(car=car)

        location = f"/api/cars/{car.id}/claims/{claim.id}"
        headers = {"Location": location}

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

    @action(detail=True, methods=["get"], url_path="history")
    def get_history(self, request, pk=None):
        """
        GET /api/cars/{carId}/history
        Returns combined chronological history of insurance policies and claims.
        """
        car = get_object_or_404(Car, pk=pk)

        # --- Fetch policies ---
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
                "date_key": p["start_date"],  # used for sorting
            }
            for p in policies
        ]

        # --- Fetch claims ---
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
                "date_key": c["claim_date"],  # used for sorting
            }
            for c in claims
        ]

        # --- Merge & sort chronologically ---
        combined = sorted(
            chain(policies_list, claims_list),
            key=itemgetter("date_key"),
        )

        # --- Remove the internal sort key ---
        for entry in combined:
            entry.pop("date_key", None)

        return Response(combined, status=status.HTTP_200_OK)