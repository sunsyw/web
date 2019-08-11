import pickle
import base64
from django_redis import get_redis_connection

# 合并请求用户的购物车数据，将未登录保存在cookie里的保存到redis中
def merge_cart_cookie_to_redis(request,user,response):
    # 获取cookie数据
    cookie_str = request.COOKIES.get('cart')
    # 如果存在
    if cookie_str is not None:
        cookie_cart = pickle.loads(base64.b64decode(cookie_str))
        # {1:{'count':1,'selected':True}}
    # 获取redis中的数据
        redis_conn = get_redis_connection('cart')
        redis_cart = redis_conn.hgetall('cart_%s'%user.id)
        cart = {}
        for sku_id,count in redis_cart.items():
            cart[int(sku_id)] = int(count)
            # {1:1,2:1}
    # 遍历cookie数据
        selected_sku_id_list = []
        for sku_id,selected_count_dict in cookie_cart.items():
            # 如果redis购物车原有商品数据,数量覆盖,如果没有,添加新记录
            cart[sku_id] = selected_count_dict['count']

            # 勾选状态的添加到列表
            if selected_count_dict['selected']:
                selected_sku_id_list.append(sku_id)

    # 保存redis数据
        pl = redis_conn.pipeline()
        pl.hmset('cart_%s'%user.id,cart)
        pl.sadd('cart_selected_%s'%user.id,*selected_sku_id_list)
        pl.execute()
    # 清空cookie中的购物车数据
        response.delete_cookie('cart')
        return response
    # 如果不存在就不用管,直接返回请求
    else:
        return response