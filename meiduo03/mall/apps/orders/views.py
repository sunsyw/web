from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from goods.models import SKU
from orders.serializers import CartSKUSerializer,PlaceOrderSerialzier,OrderSerializer
from decimal import Decimal
from rest_framework.response import Response


# 订单结算
class PlaceOrderAPIView(APIView):
    def get(self,request):
        user = request.user
        # 获取选中商品的id
        redis_conn = get_redis_connection('cart')
        redis_id = redis_conn.hgetall('cart_%s'%user.id)
        redis_selected = redis_conn.smembers('cart_selected_%s'%user.id)

        redis_selected_cart = {}
        # 将选中的商品挑出来
        for sku_id in redis_selected:
            redis_selected_cart[int(sku_id)] = int(redis_id[sku_id])
        ids = redis_selected_cart.keys() # 选中商品的id
        # 查询选中商品的信息
        skus = SKU.objects.filter(pk__in=ids)
        for sku in skus:
            sku.count = redis_selected_cart[sku.id]


        freight = Decimal('10.00')
        serializer = PlaceOrderSerialzier({'freight':freight,'skus':skus})
        return Response(serializer.data)


# 提交订单
class OrderAPIView(APIView):
    permission_classes = [IsAuthenticated]
    def post(self,request):
        data = request.data
        serializer = OrderSerializer(data=data,context={'request':request})
        serializer.is_valid()
        serializer.save()
        return Response(serializer.data)