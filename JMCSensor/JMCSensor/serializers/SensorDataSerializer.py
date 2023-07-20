from rest_framework import serializers
from ..models.SensorData import SensorData

class SensorDataSerializer(serializers.ModelSerializer):
    class Meta:
        model = SensorData
        fields = ['userId', 'gas', 'movement', 'brightness', 'humidity', 'temperature', 'pressure']
