from django.shortcuts import render

# Create your views here.

from rest_framework.viewsets import ReadOnlyModelViewSet
from areas.models import Area
from areas.serializers import AreasSerializer,SubsAreaSerializer
from rest_framework_extensions.cache.mixins import CacheResponseMixin


class AreaViewSet(CacheResponseMixin,ReadOnlyModelViewSet):
    pagination_class = None
    def get_queryset(self):
        # user = self.request.user
        # self 是视图集
        # 视图集有一个属性 action
        # action 就是  list,update,retrieve
        if self.action == 'list':
            return Area.objects.filter(parent=None)
        else:
            return Area.objects.all()

    def get_serializer_class(self):
        if self.action == 'list':
            return AreasSerializer
        else:
            return SubsAreaSerializer



