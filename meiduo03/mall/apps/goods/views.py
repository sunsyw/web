from django.shortcuts import render

# Create your views here.
from rest_framework.generics import ListAPIView
from goods.serializers import SKUSerializer
from goods.serializers import SKUIndexSerializer
from goods.models import SKU

from rest_framework.filters import OrderingFilter

from drf_haystack.viewsets import HaystackViewSet

# 热销商品
class HotsSKUListAPIView(ListAPIView):
    pagination_class = None
    serializer_class = SKUSerializer

    def get_queryset(self):
        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category_id=category_id,is_launched=True).order_by('-sales')[:2]



# 商品分页
class SKUListAPIView(ListAPIView):
    serializer_class = SKUSerializer

    # 添加排序
    filter_backends = [OrderingFilter]
    # 添加字段排序
    ordering_fields = ['sales','price','create_time']

    # 添加分页
    def get_queryset(self):
        category_id = self.kwargs['category_id']

        return SKU.objects.filter(category_id=category_id,is_launched=True)


# SKU 搜索
class SKUSearchViewSet(HaystackViewSet):
    index_models = [SKU]

    serializer_class = SKUIndexSerializer


