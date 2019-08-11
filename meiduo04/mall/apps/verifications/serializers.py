from rest_framework import serializers
from django_redis import get_redis_connection


class RegisterSmsSerializer(serializers.Serializer):
    text = serializers.CharField(label='图片验证码',max_length=4,min_length=4,required=True)
    image_code_id = serializers.UUIDField(label='uuid')

    def validate(self, attrs):
        # 获取用户提交的数据
        text = attrs.get('text')
        # 连接redis
        redis_conn = get_redis_connection('code')
        image_code_id = attrs.get('image_code_id')
        redis_text = redis_conn.get('img_'+image_code_id)
        if redis_text is None:
            raise serializers.ValidationError('图片验证码无效')
        if redis_text.decode().lower() != text.lower():
            raise serializers.ValidationError('验证码错误')
        return attrs
