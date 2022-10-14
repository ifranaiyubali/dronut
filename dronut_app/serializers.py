"""Model serializers are defined here"""
from rest_framework import serializers
from dronut_app.models import Donuts


class DonutSerializer(serializers.ModelSerializer):
    """ Donut Model serializer"""
    class Meta:
        model = Donuts
        fields = '__all__'
