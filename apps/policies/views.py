from rest_framework import viewsets, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import action
from apps.cars.models import Car
from .models import InsurancePolicy
from .serializers import InsurancePolicySerializer


class InsurancePolicyViewSet(viewsets.ModelViewSet):
    permission_classes = [IsAuthenticated]
    queryset = InsurancePolicy.objects.all().order_by("-logged_expiry_at")
    serializer_class = InsurancePolicySerializer

    @action(detail=False, methods=["post"], url_path=r"cars/(?P<car_id>\d+)/policies")
    def create_policy_for_car(self, request, car_id=None):
        """
        POST /api/cars/{carId}/policies
        Create a new insurance policy for a given car.
        """
        try:
            car = Car.objects.get(pk=car_id)
        except Car.DoesNotExist:
            return Response({"detail": "Car not found."}, status=status.HTTP_404_NOT_FOUND)

        serializer = InsurancePolicySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        start_date = serializer.validated_data["start_date"]
        end_date = serializer.validated_data["end_date"]

        # Validation: end_date must be >= start_date
        if end_date < start_date:
            return Response(
                {"detail": "end_date must be greater than or equal to start_date."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        policy = InsurancePolicy.objects.create(
            car=car,
            provider=serializer.validated_data.get("provider"),
            start_date=start_date,
            end_date=end_date,
        )

        return Response(
            InsurancePolicySerializer(policy).data,
            status=status.HTTP_201_CREATED,
        )
