import re
from users.models import User
from django.contrib.auth.backends import ModelBackend


# 自定义jwt返回数据
def jwt_response_payload_handler(token,user=None,request=None):
    return {
        'token': token,
        'username': user.username,
        'user_id': user.id
    }

# 手机登录
def get_user_by_account(account):
    try:
        if re.match(r'1[3-9]\d{9}',account):
            user = User.objects.get(mobile=account)
        else:
            user = User.objects.get(username=account)
    except User.DoesNotExist:
        user = None
    return user
# 自定义用户名或手机号认证
class UsernameMobileAuthBackend(ModelBackend):
    def authenticate(self, request, username=None, password=None, **kwargs):
        user = get_user_by_account(username)

        if user is not None and user.check_password(password):
            return user

