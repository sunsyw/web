from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from django_redis import get_redis_connection
from rest_framework.permissions import IsAuthenticated
from goods.models import SKU
from orders.serializers import PlaceOrderSerialzier,OrderSerializer,\
    OrderListSerializer,CommentGoodsSerializer,CommentsSerializer,\
    SKUCommentsSerializer
from decimal import Decimal
from rest_framework.response import Response

from orders.models import OrderInfo, OrderGoods
from orders.utils import MyPageNumberPagination


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
        ids = redis_selected_cart.keys()  # 选中商品的id
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

        # 获取订单数据
    def get(self, request):
        user = request.user
        order = OrderInfo.objects.filter(user=user).order_by('-create_time')
        pg = MyPageNumberPagination()
        page_roles = pg.paginate_queryset(queryset=order, request=request, view=self)
        serializer = OrderListSerializer(page_roles, many=True)
        count = order.count()
        return Response({'count': count, 'results': serializer.data})


# class OrderListAPIView(ListAPIView):
#     permission_classes = [IsAuthenticated]
#     filter_backends = [OrderingFilter]
#     serializer_class = OrderListSerializer
#
#     def queryset(self):
#         return OrderInfo.objects.filter(user=self.request.user)


# 商品评论页面
class CommentGoodsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self,request,order_id):
        goods_info = OrderGoods.objects.filter(order_id=order_id)
        serializer = CommentGoodsSerializer(goods_info,many=True)
        return Response(serializer.data)


# 添加评论
class CommentsAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self,request,order_id):
        data = request.data
        '''<class 'dict'>: {'order': '20190317020304000000001', 
        'sku': 5, 'comment': '11111', 'score': 5, 'is_anonymous': False} 
        '''
        sku_id = data['sku']
        serializer = CommentsSerializer(data=data,context={'order_id':order_id,'sku_id':sku_id})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# 商品评论页面
class SKUCommentsAPIView(APIView):
    def get(self,request,sku_id):
        goods = OrderGoods.objects.filter(sku_id=sku_id,is_commented=True).order_by('-create_time')
        serializer = SKUCommentsSerializer(goods,many=True)
        return Response(serializer.data)

