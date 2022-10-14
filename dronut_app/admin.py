""" Admin Module to for configuring admin items"""

from django.contrib import admin
from dronut_app.models import Donuts


# Register your models here.

class DonutDatAdmin(admin.ModelAdmin):
    """ For managing Donut Model"""
    search_fields = ['donut_code']
    list_display = ['id', 'donut_code', 'description', 'price_per_unit']


admin.site.register(Donuts, DonutDatAdmin)
