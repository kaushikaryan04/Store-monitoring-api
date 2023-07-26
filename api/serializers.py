from rest_framework import serializers
from .models import StoreStatus , TimeZone , MenuHours


class StoreStatusSerializers(serializers.Serializer):
    class Meta:
        fields = "__all__"
        model = StoreStatus

class TimeZoneSerializers(serializers.Serializer):
    class Meta:
        fields = "__all__"
        model = TimeZone

class MenuHoursSerializers(serializers.Serializer):
    class Meta:
        fields = "__all__"
        model = MenuHours