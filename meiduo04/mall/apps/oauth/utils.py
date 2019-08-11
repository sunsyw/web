
from itsdangerous import TimedJSONWebSignatureSerializer as Serializer
from mall import settings
from itsdangerous import SignatureExpired,BadSignature
from rest_framework_jwt.settings import api_settings

# 加密
def generate_openid_token(openid):
    # 1.创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=600)
    # 2.组织数据
    data = {'openid':openid}
    # 3. 加密
    token = s.dumps(data)
    return token.decode()


# 解密
def check_access_token(token):
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=600)
    try:
        result = s.loads(token)
    except BadSignature:
        return None
    access_token=result.get('access_token')
    openid=result.get('openid')
    if access_token is not None:
        return access_token
    elif openid is not None:
        return openid

# jwt
def jwt_login(user):
    # 登录状态token
    jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
    jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
    payload = jwt_payload_handler(user.user)
    token = jwt_encode_handler(payload)
    return token

def generate_access_token(access_token):
    # 1.创建序列化器
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=600)
    # 2.组织数据
    data = {'access_token':access_token}
    # 3. 加密
    token = s.dumps(data)
    return token.decode()

def check_sina_access_token(token):
    s = Serializer(secret_key=settings.SECRET_KEY,expires_in=600)
    try:
        result = s.loads(token)
    except BadSignature:
        return None
    return result.get('access_token')