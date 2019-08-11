from rest_framework import serializers

# serializers.ModelSerializer
# serializers.Serializer
from goods.models import SKU


class CartSerializer(serializers.Serializer):
    # sku_id
    # count
    # selected 选填
    sku_id = serializers.IntegerField(label='商品id',required=True,min_value=0)
    count = serializers.IntegerField(label='个数',required=True,min_value=1)
    selected = serializers.BooleanField(label='是否选中',required=False,default=True)



    def validate(self, attrs):

        sku_id = attrs.get('sku_id')
        # 什么时候加异常
        #  我们特殊讲过的异常 还有 我们获取外界数据(操作数据库,redis,文件)
        # 1. 判断商品是否存在
        try:
            sku = SKU.objects.get(pk=sku_id)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        # 2. 判断库存
        count = attrs.get('count')
        if sku.stock < count:
            raise serializers.ValidationError('库存不足')

        return attrs


from rest_framework import serializers
from goods.models import SKU

class CartSKUSerializer(serializers.ModelSerializer):

    count = serializers.IntegerField(label='数量')
    selected = serializers.BooleanField(label='是否勾选')

    class Meta:
        model = SKU
        fields = ('id','count', 'name', 'default_image_url', 'price', 'selected')
