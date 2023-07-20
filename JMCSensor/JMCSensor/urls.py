from django.contrib import admin
from django.urls import path
from .views.SensorDataView import SensorDataView
from .views.SensorListView import SensorDataListView


urlpatterns = [
    path('sensor/', SensorDataView.as_view(), name='sensor'),
    path('sensor-list/<int:userId>/', SensorDataListView.as_view(), name='sensor-data-list'),
]
