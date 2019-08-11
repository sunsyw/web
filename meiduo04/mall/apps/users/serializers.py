from rest_framework import serializers

from goods.models import SKU
from users.models import User,Address
from django_redis import get_redis_connection
import re
from rest_framework_jwt.settings import api_settings

from celery_tasks.mail.tasks import send_verify_email
from users.utils import check_sms_code

"""
用户名,手机号,密码,确认密码,短信验证码,是否同意协议
"""


class RegisterUserSerializer(serializers.ModelSerializer):

    password2=serializers.CharField(max_length=20,min_length=8,write_only=True,required=True,label='确认密码')
    sms_code=serializers.CharField(max_length=6,min_length=6,write_only=True,required=True,label='短信验证码')
    allow=serializers.CharField(write_only=True,required=True,label='是否同意协议')
    token = serializers.CharField(label='登录状态token',read_only=True)

    class Meta:
        model = User
        fields = ['username','mobile','password','allow','password2','sms_code','token']
        extra_kwargs = {
            'id': {'read_only': True},
            'username': {
                'min_length': 5,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许5-20个字符的用户名',
                    'max_length': '仅允许5-20个字符的用户名',
                }
            },
            'password': {
                'write_only': True,
                'min_length': 8,
                'max_length': 20,
                'error_messages': {
                    'min_length': '仅允许8-20个字符的密码',
                    'max_length': '仅允许8-20个字符的密码',
                }
            }
        }

    def validate_mobile(self,value):
        if not re.match(r'1[3-9]\d{9}',value):
            raise serializers.ValidationError('手机号格式不正确')
        return value

    def validate_allow(self, value):
        if value != 'true':
            raise serializers.ValidationError('未同意协议')
        return value

    def validate(self, attrs):
        password = attrs['password']
        password2 = attrs['password2']
        if password != password2:
            raise serializers.ValidationError('密码不一致')

        sms_code = attrs['sms_code']
        mobile = attrs['mobile']
        redis_conn = get_redis_connection('code')
        redis_code = redis_conn.get('sms_'+mobile)
        if redis_code is None:
            raise serializers.ValidationError('验证码过期')

        if redis_code.decode() != sms_code:
            raise serializers.ValidationError('验证码错误')

        return attrs
    # OrderedDict([('username', 'itcast'), ('mobile', '13112345679'),
    # ('password', '1234567890'), ('allow', 'true'),
    # ('password2', '1234567890'), ('sms_code', '809591')])

    def create(self, validated_data):
        del validated_data['sms_code']
        del validated_data['password2']
        del validated_data['allow']

        user = User.objects.create(**validated_data)
        # 密码加密
        user.set_password(validated_data['password'])
        user.save()

        # 登录状态token
        jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
        jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
        payload = jwt_payload_handler(user)
        token = jwt_encode_handler(payload)
        # 将token返回前端
        user.token = token
        return user


class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id','username','mobile','email','email_active']


class UserEmailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['email']
        extra_kwargs = {'email':{'required':True}}

    def update(self,instance,validated_data):
        email = validated_data.get('email')
        instance.email = email
        instance.save()

        # 发送邮件
        # 异步发送邮件
        # from django.core.mail import send_mail
        #
        # subject = '美多商城激活邮件' # 主题
        # message = '' # 内容
        # from_email = 'sunsyw@163.com'
        # recipient_list = [email]  # 收件人
        #
        #
        # token = verify_token(instance.id,email)
        # verify_url = 'http://www.meiduo.site:8080/success_verify_email.html?token=%s' % token
        # html_message = '<p>尊敬的用户您好！</p>' \
        #                '<p>感谢您使用美多商城。</p>' \
        #                '<p>您的邮箱为：%s 。请点击此链接激活您的邮箱：</p>' \
        #                '<p><a href="%s">%s<a></p>' % (email, verify_url, verify_url)
        #
        # send_mail(subject, message, from_email, recipient_list,
        #           html_message=html_message)

        send_verify_email.delay(instance.id,email)

        return instance


# 用户收货地址序列化器
class UserAddressSerializer(serializers.ModelSerializer):

    # 将地址字符串转化为id
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        # 除了
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user_id'] = user.id

        # address = Address.objects.create(**validated_data)
        address = super().create(validated_data)
        return address


class AddressTitleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['title']


class ChangeAddressSerializer(serializers.ModelSerializer):
    province = serializers.StringRelatedField(read_only=True)
    city = serializers.StringRelatedField(read_only=True)
    district = serializers.StringRelatedField(read_only=True)

    province_id = serializers.IntegerField(label='省ID', required=True)
    city_id = serializers.IntegerField(label='市ID', required=True)
    district_id = serializers.IntegerField(label='区ID', required=True)
    mobile = serializers.RegexField(label='手机号', regex=r'^1[3-9]\d{9}$')

    class Meta:
        model = Address
        exclude = ('user', 'is_deleted', 'create_time', 'update_time')

    def update(self, instance, validated_data):
        instance.receiver = validated_data.get('receiver')
        instance.place = validated_data.get('place')
        instance.mobile = validated_data.get('mobile')
        instance.tel = validated_data.get('tel')
        instance.email = validated_data.get('email')
        instance.city_id = validated_data.get('city_id')
        instance.district_id = validated_data.get('district_id')
        instance.province_id = validated_data.get('province_id')
        instance.save()
        return instance


# 浏览记录序列化器
class UserHistorySerializer(serializers.Serializer):
    sku_id = serializers.IntegerField(label='商品',required=True)

    # 验证
    def validate_sku_id(self, value):
        try:
            SKU.objects.get(pk=value)
        except SKU.DoesNotExist:
            raise serializers.ValidationError('商品不存在')
        return value

    # 保存在redis中
    def create(self, validated_data):
        user = self.context['request'].user
        sku_id = validated_data.get('sku_id')

        # 连接redis
        redis_conn = get_redis_connection('history')

        # 保存记录之前，先删除重复记录
        redis_conn.lrem('history_%s' % user.id,0,sku_id)
        # 保存数据 从左边添加
        redis_conn.lpush('history_%s' % user.id,sku_id)
        # 只保留5条记录
        redis_conn.ltrim('history_%s' % user.id,0,4)
        return validated_data


class SKUSerializer(serializers.ModelSerializer):

    class Meta:
        model = SKU
        fields = ('id', 'name', 'price', 'default_image_url', 'comments')


from django_redis import get_redis_connection

class CheckImageCodeSerialzier(serializers.Serializer):
    """
    图片验证码校验序列化器
    """
    def validate(self, attrs):
        """校验图片验证码是否正确"""

        redis_conn = get_redis_connection('code')
        # 在此处修改
        # 60s内是否有发送记录
        mobile = self.context['view'].kwargs.get('mobile')
        if mobile:
            send_flag = redis_conn.get('send_flag_%s' % mobile)
            if send_flag:
                raise serializers.ValidationError('发送短信次数过于频繁')

        return attrs


class SmscodeSerializer(serializers.Serializer):

    sms_code = serializers.CharField(label='短信验证码')

    # 短信验证码
    def validate(self, attrs):
        mobile = self.context['mobile']
        if not re.match(r'1[3-9]\d{9}',mobile):
            raise serializers.ValidationError('手机号格式错误')
        # 短信验证码
        # 获取用户输入的数据
        sms_code = attrs['sms_code']

        sRet = check_sms_code(sms_code, mobile)
        if sRet == 'TimeOut':
            raise serializers.ValidationError('短信验证码已过期')

        elif sRet == 'ValueError':
            raise serializers.ValidationError('短信验证码输入有误')

        return attrs


class PasswordSerializer(serializers.ModelSerializer):
    password2 = serializers.CharField(label='校验密码', allow_null=False, allow_blank=False, write_only=True)

    class Meta:
        model = User
        fields = ('password','password2', )

    def validate(self, attrs):
        # 验证密码和确认密码
        # 获取数据
        password = attrs.get('password')
        password2 = attrs.get('password2')
        # 比对
        if password != password2:
            raise serializers.ValidationError('两次输入密码不一致')
        del attrs['password2']
        return attrs

    def update(self, instance, validated_data):
        password = validated_data.get('password')
        instance.set_password(password)
        instance.save()
        return instance



