from itsdangerous import TimedJSONWebSignatureSerializer
from mall import settings
from itsdangerous import BadSignature

def verify_token(id,email):
    s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires_in=3600)
    token = s.dumps({'id':id,'email':email})
    return token.decode()

def decode_token(token):
    s = TimedJSONWebSignatureSerializer(settings.SECRET_KEY,expires_in=3600)
    try:
        result = s.loads(token)
    except BadSignature:
        return None
    return result