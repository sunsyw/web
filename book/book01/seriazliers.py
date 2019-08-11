from rest_framework import serializers
from book01.models import BookInfo


class IndexSerializers(serializers.ModelSerializer):
    class Meta:
        model = BookInfo
        fields = '__all__'

