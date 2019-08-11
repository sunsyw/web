from django_redis import get_redis_connection
from rest_framework import serializers
from oauth.utils import check_access_token
from users.models import User
from oauth.models import OAuthQQUser


class OauthQQUserSerializer(serializers.Serializer):
    access_token = serializers.CharField(label='操作凭证')
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')
    password = serializers.CharField(label='密码', max_length=20, min_length=8)
    sms_code = serializers.CharField(label='短信验证码')

    def validate(self, attrs):
        access_token = attrs['access_token']
        openid = check_access_token(access_token)
        if openid is None:
            raise serializers.ValidationError('openid过期')
        # 将openid添加到attrs中
        attrs['openid'] = openid

        # 2.短信验证码

        sms_code = attrs.get('sms_code')
        # 连接redis
        redis_conn = get_redis_connection('code')
        # 获取数据
        mobile = attrs.get('mobile')
        redis_code = redis_conn.get('sms_' + mobile)
        # 判断数据是否存在
        if redis_code is None:
            raise serializers.ValidationError('短信验证码已过期')
        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('短信验证码输入错误')

        # 3.判断用户
        try:
            user = User.objects.get(mobile=mobile)
        except User.DoesNotExist:
            pass
        else:
            password = attrs['password']
            if not user.check_password(password):
                raise serializers.ValidationError('密码不正确')
            attrs['user'] = user
        return attrs

    def create(self, validated_data):
        user = validated_data.get('user')
        if user is None:
            user = User.objects.create(
                username=validated_data.get('mobile'),
                mobile=validated_data.get('mobile'),
                password=validated_data.get('password')
            )
            user.set_password(validated_data.get('password'))
            user.save()
        qquser = OAuthQQUser.objects.create(
            user = user,
            openid = validated_data.get('openid')
        )
        return qquser