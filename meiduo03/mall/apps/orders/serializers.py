from decimal import Decimal
from rest_framework import serializers

from goods.models import SKU
from django.utils import timezone
from django_redis import get_redis_connection

from django.db import transaction

class CartSKUSerializer(serializers.ModelSerializer):
    """
    购物车商品数据序列化器
    """
    count = serializers.IntegerField(label='数量')

    class Meta:
        model = SKU
        fields = ('id', 'name', 'default_image_url', 'price', 'count')


class PlaceOrderSerialzier(serializers.Serializer):
    freight = serializers.DecimalField(label='运费',decimal_places=2,max_digits=10)
    skus = CartSKUSerializer(many=True)


from orders.models import OrderInfo, OrderGoods


class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderInfo
        fields = ('order_id', 'address', 'pay_method')
        read_only_fields = ('order_id',)
        extra_kwargs = {
            'address': {
                'write_only': True,
                'required': True,
            },
            'pay_method': {
                'write_only': True,
                'required': True
            }
        }

    def create(self, validated_data):
        user = self.context['request'].user
        address = validated_data.get('address')
        order_id = timezone.now().strftime('%Y%m%d%H%M%S') + '%09d'%user.id
        total_count = 0
        total_amount = Decimal('0')
        freight = Decimal('10.00')
        pay_method = validated_data.get('pay_method')
        if pay_method == OrderInfo.PAY_METHODS_ENUM['CASH']:
            status = OrderInfo.ORDER_STATUS_ENUM['UNSEND']
        else:
            status = OrderInfo.ORDER_STATUS_ENUM['UNPAID']

        # 事物
        with transaction.atomic():
            save_point = transaction.savepoint()

            order = OrderInfo.objects.create(
                order_id=order_id,
                user=user,
                address=address,
                total_count=total_count,
                total_amount=total_amount,
                freight=freight,
                pay_method=pay_method,
                status=status
            )

            # 从redis中获取数据
            redis_conn = get_redis_connection('cart')
            redis_id_counts = redis_conn.hgetall('cart_%s'%user.id)
            redis_selected_ids = redis_conn.smembers('cart_selected_%s'%user.id)

            redis_selecteds = {}
            for sku_id in redis_selected_ids:
                redis_selecteds[int(sku_id)] = int(redis_id_counts[sku_id])
            # {sku_id:count}

            # 获取sku_id  ids=[1,2,3]
            ids = redis_selecteds.keys()
            # 查询商品的信息
            skus = SKU.objects.filter(pk__in=ids)

            # 遍历每个数据
            for sku in skus:
                count = redis_selecteds[sku.id]
                if sku.stock < count:   # 商品库存小于数量
                    raise serializers.ValidationError('库存不足')

                # sku.stock -= count
                # sku.sales += count
                # sku.save()

                # 乐观锁
                # 原始数据
                origin_stock = sku.stock
                origin_sales = sku.sales

                new_stock = origin_stock - count
                new_sales = origin_sales + count
                # 查询数据库，如果原始数据发生变化则无法更新，没发生变化则更新数据
                ret = SKU.objects.filter(id=sku.id,stock=origin_stock).update(stock=new_stock,sales=new_sales)
                if ret == 0:
                    transaction.savepoint_rollback(save_point)
                    raise ValueError('下单失败')

                # 修改订单数量和价格
                order.total_count += count
                order.total_amount += count * sku.price

                OrderGoods.objects.create(
                    order=order,
                    sku=sku,
                    count=count,
                    price=sku.price
                )
            order.save()

            # 下单成功 提交
            transaction.savepoint_commit(save_point)
        return order


