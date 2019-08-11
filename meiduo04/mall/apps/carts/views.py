from django.shortcuts import render

# Create your views here.


from rest_framework.views import APIView
from carts.serializers import CartSerializer,CartSKUSerializer
from django_redis import get_redis_connection
from rest_framework.response import Response
import base64
import pickle

from goods.models import SKU

from rest_framework import status

'''
1 获取信息
2 验证
3 登陆用户保存在reids
4 未登录用户保存在cookie
5 返回

'''

class CartAPIView(APIView):
    def perform_authentication(self, request):
        pass

    def post(self,request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        try:
            user = request.user
        except Exception:
            user = None
        # 判断用户是否登陆
        # 如果登陆并通过验证 将数据保存在redis中
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            # redis_conn.hset('cart_%s'%user.id,sku_id,count)
            # 累加
            # redis_conn.hincrby('cart_%s'%user.id,sku_id,count)
            #
            # if selected:
            #     redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            #     return Response(serializer.data)

            # redis管道
            pl = redis_conn.pipeline()
            pl.hincrby('cart_%s' % user.id, sku_id, count)
            if selected:
                pl.sadd('cart_selected_%s'%user.id,sku_id)
            pl.execute()
            return Response(serializer.data)

        # 未登录保存在cookies中
        else:
            cookie_str = request.COOKIES.get('cart')
            # 如果有cookie 解密
            if cookie_str is not None:
                bytes_data = base64.b64decode(cookie_str)
                cookie_cart = pickle.loads(bytes_data)
            # 如果没有 cookie
            else:
                cookie_cart = {}

            #         cookie_cart = {1:{'count':2,'selected':True}}
            # 如果有则把前段传过来的个数累加
            if sku_id in cookie_cart:
                original_count = cookie_cart[sku_id]['count']
                count += original_count

            # 更新数据
            cookie_cart[sku_id] = {
                'count':count,
                'selected':selected
            }

            # 加密
            bytes_dumps = pickle.dumps(cookie_cart)
            bytes_str = base64.b64encode(bytes_dumps)
            cookie_save_str = bytes_str.decode()
            # 设置cookie
            response = Response(serializer.data)
            response.set_cookie('cart',cookie_save_str,3600)
            return response

    # 购物车页面
    def get(self,request):
        try:
            user = request.user
        except Exception:
            user = None

        # 登陆用户
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            redis_cart = redis_conn.hgetall('cart_%s'%user.id)
            # 1:{sku_id:1,count:1}
            redis_selected = redis_conn.smembers('cart_selected_%s'%user.id)
            # 1:{1,2,3}
            cart = {}
            for sku_id,count in redis_cart.items():
                cart[int(sku_id)] = {
                    'count':int(count),
                    'selected':sku_id in redis_selected
                }
                # {1: {'count': 1, 'selected': True}}

        # 未登录用户
        else:
            cookie_str = request.COOKIES.get('cart')
            if cookie_str is not None:
                cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cart = {}

        # 获取商品的信息
        skus = SKU.objects.filter(id__in = cart.keys())
        # 修改信息
        for sku in skus:
            sku.count = cart[sku.id]['count']
            sku.selected = cart[sku.id]['selected']

        serializer = CartSKUSerializer(skus,many=True)
        return Response(serializer.data)

    # 修改购物车信息
    def put(self,request):
        serializer = CartSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        sku_id = serializer.data.get('sku_id')
        count = serializer.data.get('count')
        selected = serializer.data.get('selected')

        try:
            user = request.user
        except Exception:
            user = None
        # 如果用户登陆 则更新redis数据 覆盖
        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            redis_conn.hset('cart_%s'%user.id,sku_id,count)
            # 改变选中状态
            if selected:
                redis_conn.sadd('cart_selected_%s'%user.id,sku_id)
            else:
                redis_conn.srem('cart_selected_%s' % user.id, sku_id)
            return Response(serializer.data)

        # 没有登陆
        else:
            cart = request.COOKIES.get('cart')
            # 解密
            if cart is not None:
                cookie_cart = pickle.loads(base64.b64decode(cart))
            else:
                cookie_cart = {}
            # 便利数据并更新
            if sku_id in cookie_cart:
                cookie_cart[sku_id] = {
                    'count':count,
                    'selected':selected
                }
            # 加密
            cookie = base64.b64encode(pickle.dumps(cookie_cart)).decode()
            # 设置cookie
            response = Response(serializer.data)
            response.set_cookie('cart',cookie,3600)

            return response

    # 删除
    def delete(self,request):
        data = request.data
        sku_id = data.get('sku_id')
        try:
            user = request.user
        except Exception:
            user = None

        if user is not None and user.is_authenticated:
            redis_conn = get_redis_connection('cart')
            redis_conn.hdel('cart_%s'%user.id,sku_id)
            redis_conn.srem('cart_selected_%s'%user.id,sku_id)
            return Response(status=status.HTTP_204_NO_CONTENT)

        else:
            cookie_str = request.COOKIES.get('cart')
            if cookie_str is not None:
                cookie_cart = pickle.loads(base64.b64decode(cookie_str))
            else:
                cookie_cart = {}

            if sku_id in cookie_cart:
                del cookie_cart[sku_id]

            cookie_save_cart = base64.b64encode(pickle.dumps(cookie_cart)).decode()

            response = Response(status=status.HTTP_204_NO_CONTENT)
            response.set_cookie('cart',cookie_save_cart,3600)
            return response



