from rest_framework import serializers
from areas.models import Area


class AreasSerializer(serializers.ModelSerializer):
    class Meta:
        model = Area
        fields = ['id','name']


class SubsAreaSerializers(serializers.ModelSerializer):

    # subs = area_set [1,2,3,...]
    subs = AreasSerializer(many=True,read_only=True)
    class Meta:
        model = Area
        fields = ['subs','id','name']


