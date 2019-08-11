import re

from django_redis import get_redis_connection
from itsdangerous import TimedJSONWebSignatureSerializer as TJWSSerializer
from mall import settings
from itsdangerous import BadSignature

from users.models import User


def verify_token(id,email):
    s = TJWSSerializer(settings.SECRET_KEY,expires_in=3600)
    token = s.dumps({'id':id,'email':email})
    return token.decode()


def decode_token(token):
    s = TJWSSerializer(settings.SECRET_KEY,expires_in=3600)
    try:
        result = s.loads(token)
    except BadSignature:
        return None
    return result

def check_sms_code(sms_code,mobile):
    # 短信验证码
    # 获取redis中的数据
    # 连接redis
    sRet = 'OK'
    redis_conn = get_redis_connection('code')
    # 获取数据
    mobile = mobile
    redis_code = redis_conn.get('sms_%s'%mobile)
    # 判断数据是否在有效期
    if redis_code is None:
        # raise serializers.ValidationError('短信验证码已过期')
        sRet ='TimeOut'
        return sRet
    # 比对
    if redis_code.decode() != sms_code:
        # raise serializers.ValidationError('短信验证码输入有误')
        sRet ='ValueError'
        return sRet
    # 返回响应
    return sRet



def get_user_by_account(username):
    try:
        if re.match(r'1[3-9]\d{9}', username):
            # 手机号
            user = User.objects.get(mobile=username)
        else:
            # 用户名
            user = User.objects.get(username=username)
    except User.DoesNotExist:
        user = None

    return user


def create_access_token_from_user(user):

    # 创建序列化器
    serializer = TJWSSerializer(secret_key=settings.SECRET_KEY,expires_in=60*10)
    # 组织数据
    data = {
        'token':user
    }
    # 加密
    token = serializer.dumps(data)
    token = token.decode()
    # 返回字符串
    return token

def check_access_token_to_mobile(access_token):
    # 1.创建序列化器
    serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=60*10)
    # 2.解密 有可能存在异常
    try:
        data = serializer.loads(access_token)
        mobile = data['mobile']
        # 3.返回数据
        return mobile
    except BadSignature:
        return None

def check_access_token_to_user_id(access_token):
    # 1.创建序列化器
    serializer = TJWSSerializer(secret_key=settings.SECRET_KEY, expires_in=60*10)
    # 2.解密 有可能存在异常
    try:
        data = serializer.loads(access_token)
        user_id = data['token']
        # 3.返回数据
        return user_id
    except BadSignature:
        return None


