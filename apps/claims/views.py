from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action

from apps.cars.models import Car
from .models import Claim
from .serializers import ClaimSerializer


class ClaimViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = Claim.objects.all().order_by("-claim_date")
    serializer_class = ClaimSerializer

    @action(detail=False, methods=["post"], url_path=r"cars/(?P<car_id>\d+)/claims")
    def create_claim_for_car(self, request, car_id=None):
        """
        POST /api/cars/{carId}/claims
        Create a new insurance claim for a given car.
        """
        # Check if car exists
        try:
            car = Car.objects.get(pk=car_id)
        except Car.DoesNotExist:
            return Response({"detail": "Car not found."}, status=status.HTTP_404_NOT_FOUND)

        # Validate serializer
        serializer = ClaimSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Save claim linked to car
        claim = serializer.save(car=car)

        # Include Location header for REST compliance
        location = f"/api/cars/{car.id}/claims/{claim.id}"
        headers = {"Location": location}

        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
