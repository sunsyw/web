from django.shortcuts import render

# Create your views here.

from rest_framework.viewsets import  ReadOnlyModelViewSet
from areas.models import Area
from areas.serializers import AreasSerializer,SubsAreaSerializers
from rest_framework_extensions.cache.mixins import CacheResponseMixin

class AreasAPIView(CacheResponseMixin,ReadOnlyModelViewSet):
    def get_queryset(self):
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AreasSerializer
        else:
            return SubsAreaSerializers
