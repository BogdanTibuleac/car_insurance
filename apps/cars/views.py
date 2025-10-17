from rest_framework import viewsets
from .models import Car
from .serializers import CarSerializer

class CarViewSet(viewsets.ModelViewSet):
    queryset = Car.objects.all().order_by("-created_at")
    serializer_class = CarSerializer
