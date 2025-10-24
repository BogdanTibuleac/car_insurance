from django.contrib.auth.models import User
from django.shortcuts import render
from rest_framework import generics

from .serializers import RegisterSerializer


class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
# Create your views here.
