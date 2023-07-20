from rest_framework import generics
from ..serializers.SensorDataSerializer import SensorDataSerializer

class SensorDataView(generics.CreateAPIView):
    serializer_class = SensorDataSerializer
