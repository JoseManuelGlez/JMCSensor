from django.db import models

class SensorData(models.Model):
    userId = models.IntegerField()
    gas = models.FloatField()
    movement = models.BooleanField()
    brightness = models.IntegerField()
    humidity = models.FloatField()
    temperature = models.FloatField()
    pressure = models.FloatField()

    class Meta:
        db_table = 'sensors'

    def __str__(self):
        return str(self.userId)
