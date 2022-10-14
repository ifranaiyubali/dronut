""" API endpoint test cases for Dronut App"""
from decimal import Decimal
from django.urls import reverse
from rest_framework.test import APITestCase
from tests.data_setup import DonutsDataSetup


class DronutsDataViewSetTests(APITestCase):
    """ Class for testing Dronuts Data View"""

    def setUp(self):
        self.url_list = 'dronut_app:donuts-list'
        self.url_quotes = 'dronut_app:donuts-quotes'
        self.url_detail = 'dronut_app:donuts-detail'
        self.response = None
        self.donut_objs = DonutsDataSetup().setup_donuts_data()
        super().setUp()

    def test_retrieve_donuts_list(self):
        """
        DronutsDataViewSet: Test to verify API endpoint for a list of Donuts
        """
        self.response = self.client.get(reverse(self.url_list), format='json')
        self.assertEqual(len(self.response.data), 2)
        self.assertEqual(self.response.data[0]['donut_code'], 'THE_HOMER')
        self.assertEqual(self.response.data[0]['price_per_unit'], '8.50')

    def test_get_donut_information(self):
        """
        DronutsDataViewSet: Test to verify API endpoint for retrieving a donut information
        """
        self.response = self.client.get(reverse(self.url_detail,
                                                kwargs={'pk': self.donut_objs[1].id}),
                                        format='json')
        self.assertEqual(self.response.data['donut_code'], 'THE_MARGIE')
        self.assertEqual(self.response.data['price_per_unit'], '10.50')

    def test_query_by_donut_code(self):
        """
        DronutsDataViewSet: Test to verify API endpoint for retrieving
        a donut information by querying donut code
        """
        self.response = self.client.get(reverse(self.url_list) + '?q=THE_MAR', format='json')
        self.assertEqual(self.response.data[0]['donut_code'], 'THE_MARGIE')
        self.assertEqual(self.response.data[0]['price_per_unit'], '10.50')

    def test_donut_creation(self):
        """
        DronutsDataViewSet: Test to verify API endpoint for creating donut
        """
        data = {
            "donut_code": "THE_HOMER_2_POINT_O",
            "description": "Best thing come in seconds , with extra chocolate topping",
            "price_per_unit": "8.20"
        }
        self.response = self.client.post(reverse(self.url_list), data=data)
        self.assertEqual(self.response.data['donut_code'], 'THE_HOMER_2_POINT_O')
        self.assertEqual(self.response.data['price_per_unit'], '8.20')

    def test_donut_updated(self):
        """
        DronutsDataViewSet: Test to verify API endpoint for updating donut
        """
        data = {
            "price_per_unit": "11.00"
        }
        self.response = self.client.patch(reverse(self.url_detail,
                                                  kwargs={'pk': self.donut_objs[1].id}), data=data)
        self.assertEqual(self.response.data['donut_code'], 'THE_MARGIE')
        self.assertEqual(self.response.data['price_per_unit'], '11.00')

    def test_get_donut_quote(self):
        """
        DronutsDataViewSet: Test to verify API endpoint for getting quote
        """
        data = {
            "donuts": [
                {
                    "donut_code": "THE_HOMER",
                    "quantity": 3
                },
                {
                    "donut_code": "THE_MARGIE",
                    "quantity": 10
                }
            ]
        }
        self.response = self.client.post(reverse(self.url_quotes), data=data, format='json')
        self.assertEqual(self.response.data['quote_line_item'][0]['donut_code'], 'THE_HOMER')
        self.assertEqual(self.response.data['quote_line_item'][0]['line_value'], Decimal('25.50'))
        self.assertEqual(self.response.data['quote_line_item'][1]['donut_code'], 'THE_MARGIE')
        self.assertEqual(self.response.data['quote_line_item'][1]['line_value'], Decimal('105.00'))
        self.assertEqual(self.response.data['quote_total'], Decimal('130.50'))

    def test_get_donut_quote_error(self):
        """
        DronutsDataViewSet: Test to verify API endpoint for getting quote errors
        """
        data = {}
        self.response = self.client.post(reverse(self.url_quotes), data=data, format='json')
        self.assertEqual(self.response.data['info'], 'Error encountered')
