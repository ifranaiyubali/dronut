""" Models are defined here"""
import uuid
from django.db import models


# Create your models here.

class Donuts(models.Model):
    """ Donut Model to store donut information"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4,
                          editable=False, verbose_name="ID", max_length=500)
    donut_code = models.CharField(max_length=50, verbose_name='Donut Code', unique=True)
    description = models.TextField(blank=True, null=True)
    price_per_unit = models.DecimalField(decimal_places=2, max_digits=12)

    class Meta:
        db_table = 'donuts'
        verbose_name = 'donut'
        verbose_name_plural = 'donuts'
