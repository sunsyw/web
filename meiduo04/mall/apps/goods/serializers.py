from rest_framework import serializers

from goods.models import SKU

from goods.search_indexes import SKUIndex
from drf_haystack.serializers import HaystackSerializer


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')


class SKUIndexSerializer(HaystackSerializer):

    class Meta:
        index_classes = [SKUIndex]
        fields = ('text', 'id', 'name', 'price', 'default_image_url', 'comments')
