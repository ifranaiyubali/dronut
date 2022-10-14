""" Module for building API end points"""
from rest_framework import viewsets, permissions, decorators, response
from django_filters.rest_framework import DjangoFilterBackend
from dronut_app.models import Donuts
from dronut_app.serializers import DonutSerializer


class DronutsDataViewSet(viewsets.ModelViewSet):  # pylint: disable=too-many-ancestors
    """ API endpoints to create, update , delete Dronut data"""
    queryset = Donuts.objects.all()
    serializer_class = DonutSerializer
    permission_classes = [permissions.AllowAny]  # TODO : Add authentication and change permissions
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['donut_code']

    def get_queryset(self):
        query_val = self.request.query_params.get('q')
        # if there is q query parameter then filter by it
        if query_val is not None:
            return self.queryset.filter(donut_code__istartswith=query_val)
        return self.queryset

    @decorators.action(detail=False, methods=['post'])
    def quotes(self, request):
        """ API end point for getting donut quotes"""
        try:
            req_data = request.data['donuts']
            quote_line_item = []
            quote_total = 0
            # Iterate over the request data
            # Check if the donut code exists in table and quantity is an integer
            # build line item from the donut code and multiply quantity by donut price
            # return the json response with line item and total
            # if there are exceptions return json format error
            for donut_item in req_data:
                donut_obj = self.queryset.filter(donut_code=donut_item['donut_code']).first()
                if donut_obj and isinstance(donut_item['quantity'], int):
                    line_value = donut_obj.price_per_unit * donut_item['quantity']
                    line_item = {'donut_code': donut_obj.donut_code,
                                 'line_value': line_value}
                    quote_line_item.append(line_item)
                    quote_total += line_value
        except Exception as exc:
            return response.Response({'error': str(exc), 'info': 'Error encountered'})
        return response.Response({'quote_line_item': quote_line_item, 'quote_total': quote_total})
