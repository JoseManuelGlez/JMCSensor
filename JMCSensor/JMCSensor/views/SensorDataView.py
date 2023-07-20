from rest_framework import generics
from ..serializers.SensorDataSerializer import SensorDataSerializer
from rest_framework.response import Response
import jwt

class SensorDataView(generics.CreateAPIView):
    serializer_class = SensorDataSerializer
