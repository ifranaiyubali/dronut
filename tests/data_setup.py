""" Module for setting db data"""
from dronut_app.models import Donuts


class DonutsDataSetup:
    """ Setup Donuts Model data"""

    def __str__(self):
        return self.__class__.__name__

    def setup_donuts_data(self):
        """ crate a Donut record for use in testing"""
        donut_obj = []
        donuts_kwargs = [
            {
                'donut_code': 'THE_HOMER',
                'description': 'cream filled donut with sprinkles',
                'price_per_unit': 8.50,
            },
            {
                'donut_code': 'THE_MARGIE',
                'description': """Head High stacked goodies, with a twist of attitude,\n"""
                               """a bit more expensive since woman are more fashionable """,
                'price_per_unit': 10.50,
            }
        ]

        for data in donuts_kwargs:
            obj = Donuts.objects.create(**data)
            donut_obj.append(obj)
        return donut_obj
