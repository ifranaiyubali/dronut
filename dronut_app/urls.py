""" Dronut app urls are defined here"""
from django.urls import path, include
from rest_framework import routers
from dronut_app import api

router = routers.DefaultRouter()
router.register(r'donuts', api.DronutsDataViewSet)

url_patterns = [
    path('', include(router.urls)),
]
