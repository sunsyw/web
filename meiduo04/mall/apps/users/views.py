import re

from django.shortcuts import render

# Create your views here.
from django_redis import get_redis_connection
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import GenericViewSet

from goods.models import SKU
from users.models import User, Address
from users.serializers import RegisterUserSerializer, \
    UserDetailSerializer, UserEmailSerializer, UserAddressSerializer, \
    AddressTitleSerializer, ChangeAddressSerializer, \
    UserHistorySerializer, SKUSerializer, CheckImageCodeSerialzier, SmscodeSerializer, PasswordSerializer
from rest_framework.generics import GenericAPIView
from rest_framework.mixins import CreateModelMixin
from rest_framework.generics import CreateAPIView, RetrieveAPIView, UpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework import status, mixins
from users.utils import decode_token, create_access_token_from_user, check_access_token_to_user_id

from rest_framework_jwt.views import ObtainJSONWebToken
from carts.utils import merge_cart_cookie_to_redis

# 用户名
from utils.users import get_user_by_account
from verifications.serializers import RegisterSmsSerializer


class RegisterUsernameAPI(APIView):
    def get(self, request, username):
        count = User.objects.filter(username=username).count()
        context = {'count': count, 'username': username}
        return Response(context)


# 密码
class RegisterPhoneAPI(APIView):
    def get(self, request, mobile):
        count = User.objects.filter(mobile=mobile).count()
        context = {'count': count, 'mobile': mobile}
        return Response(context)


# 注册
# 一级视图
# class RegisterUserAPI(APIView):
#     def post(self,request):
#         data = request.data
#         serializer = RegisterUserSerializer(data=data)
#         serializer.is_valid()
#         serializer.save()
#         return Response(serializer.data)
#
# 二级视图
# class RegisterUserGAPI(CreateModelMixin,GenericAPIView):
#     serializer_class = RegisterUserSerializer
#     def post(self,request):
#         return self.create(request)


# 三级视图
class RegisterUserTAPI(CreateAPIView):
    serializer_class = RegisterUserSerializer


# 用户中心
# 一级视图
# class UserDetailAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     def get(self,request):
#         user = request.user
#         serializer = UserDetailSerializer(user)
#         return Response(serializer.data)

class UserDetailAPIView(RetrieveAPIView):
    # 判断用户登录
    permission_classes = [IsAuthenticated]

    serializer_class = UserDetailSerializer

    # RetrieveAPIView中缺少pk参数，所以重写get_object方法
    def get_object(self):
        return self.request.user


# 邮箱验证
# class UserEmailAPIView(APIView):
#     permission_classes = [IsAuthenticated]
#     def put(self,request):
#         data = request.data
#         serializer = UserEmailSerializer(instance=request.user,data=data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

class UserEmailAPIView(UpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = UserEmailSerializer

    def get_object(self):
        return self.request.user


class UserEmailVerificationAPIView(APIView):
    def get(self, request):
        # 1 接收token
        token = request.query_params.get('token')
        if token is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 2 解密
        result = decode_token(token)  # {'id': 2, 'email': 'sunsyw@163.com'}
        # 3 查询用户信息
        id = result.get('id')
        email = result.get('email')
        try:
            user = User.objects.get(id=id, email=email)
        except User.DoesNotExist:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 4 更改用户信息
        user.email_active = True
        user.save()
        # 5 返回响应
        return Response({'msg': 'ok'})


"""
    用户地址新增与修改
    GET: /users/addresses/
    POST: /users/addresses/
    DELETE: /users/addresses/
    PUT: /users/addresses/pk/status/
    PUT: /users/addresses/pk/title/
"""


# 一级视图
class UserAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    # 添加收获地址
    def post(self, request):
        data = request.data
        serializer = UserAddressSerializer(data=data, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    # 获取收获地址
    def get(self, request):
        user = request.user
        queryset = Address.objects.filter(user_id=user.id)
        serializer = UserAddressSerializer(queryset, many=True)
        user = self.request.user
        return Response({
            'user_id': user.id,
            'addresses': serializer.data,
        })


# 修改，删除地址
class ChangeAddressAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        address = Address.objects.get(id=pk)
        data = request.data
        serializer = ChangeAddressSerializer(instance=address, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def delete(self, request, pk):
        address = Address.objects.get(id=pk)
        address.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


# 修改title信息
class AddressTitleAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        address = Address.objects.get(id=pk)
        data = request.data
        serializer = AddressTitleSerializer(instance=address, data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)


# 设置默认地址
class AddressStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, pk):
        address = Address.objects.get(id=pk)
        user = self.request.user
        user.default_address = address
        request.user.save()
        return Response({'msg': 'ok'})


# 添加收获地址
# 三级视图
# class UserAddressAPIView(CreateAPIView,RetrieveAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserAddressSerializer()


# 浏览记录
# class UserHistoryAPIView(CreateAPIView):
#     permission_classes = [IsAuthenticated]
#     serializer_class = UserHistorySerializer

class UserHistoryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        data = request.data
        serializer = UserHistorySerializer(data=data, context={'request': request, 'view': self})
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data)

    def get(self, request):
        # 获取用户信息
        user = self.request.user
        user_id = user.id
        # 连接redis
        redis_conn = get_redis_connection('history')
        # 获取数据
        history_sku_ids = redis_conn.lrange('history_%s' % user_id, 0, 5)
        skus = []
        for sku_id in history_sku_ids:
            sku = SKU.objects.get(pk=sku_id)
            skus.append(sku)
        # 序列化
        serializer = SKUSerializer(skus, many=True)
        return Response(serializer.data)


# 登陆合并购物车
class UserAuthorizationView(ObtainJSONWebToken):
    def post(self, request):
        # 调用jwt扩展的方法，对用户登录的数据进行验证
        response = super().post(request)
        # 如果用户登录成功，进行购物车数据合并
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # 表示用户登录成功
            user = serializer.validated_data.get('user')
            # 合并购物车
            response = merge_cart_cookie_to_redis(request, user, response)
        return response


#  修改密码

class UpdatePasswdView(APIView):

    def put(self, request, pk):
        data = request.data
        user = User.objects.get(id=pk)
        if not user.check_password(data['old_password']):
            raise Exception('原密码输入有误')
        if data['password'] != data['password2']:
            raise Exception('两次密码不一致，请重新输入')
        user.set_password(data['password'])
        user.save()
        return Response({'message': 'ok'})


class SMSCodeTokenView(GenericAPIView):
    """
    根据账号和图片验证码，获取发送短信的token
    """
    serializer_class = CheckImageCodeSerialzier

    def get(self, request, account):
        serializer = self.get_serializer(data=request.query_params)
        serializer.is_valid(raise_exception=True)

        user = get_user_by_account(account)  # 通过手机号或用户名获取用户名
        if user is None:
            return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)

        # 生成发送短信的access_token
        access_token = user.generate_send_sms_code_token()

        # 处理手机号
        mobile = re.sub(r'(\d{3})\d{4}(\d{3})', r'\1****\2', user.mobile)
        return Response({'mobile': mobile, 'access_token': access_token})


#
# class SMSCodeTokenView(GenericAPIView):
#     """
#     根据账号和图片验证码，获取发送短信的token
#     """
#     serializer_class = CheckImageCodeSerialzier
#
#     def get(self, request, account):
#         serializer = self.get_serializer(data=request.query_params)
#         serializer.is_valid(raise_exception=True)
#
#         user = get_user_by_account(account)
#         if user is None:
#             return Response({'message': '用户不存在'}, status=status.HTTP_404_NOT_FOUND)
#
#         # 生成发送短信的access_token
#         # access_token = user.generate_send_sms_code_token()
#         query_params = request.query_params
#         serializer = CheckImageCodeSerialzier(data=query_params)
#         serializer.is_valid(raise_exception=True)
#         from rest_framework_jwt.settings import api_settings
#         # ① 获取 jwt的2个方法
#         jwt_payload_handler = api_settings.JWT_PAYLOAD_HANDLER
#         jwt_encode_handler = api_settings.JWT_ENCODE_HANDLER
#         # ② 将user信息 传递给 payload方法
#         payload = jwt_payload_handler(user)
#         # ③ 对payload返回的数据进行编码,编码之后就是token
#         token = jwt_encode_handler(payload)
#         mobile = re.sub(r'(\d{3})\d{4}(\d{3})', r'\1****\2', user.mobile)
#         data = {'mobile': mobile, 'access_token': token}
#         return Response(data=data)


# 找回密码第三步
class FindPasswordThirdAPIView(APIView):
    def get(self,request,username):
        user = get_user_by_account(username)
        mobile = user.mobile
        data = request.query_params.dict()
        serializer = SmscodeSerializer(data=data,context={'mobile':mobile})
        serializer.is_valid(raise_exception=True)
        # user = User.objects.get(username=username)
        user_id = user.id
        access_token = create_access_token_from_user(user_id)
        context = {
            'user_id':user_id,
            'access_token':access_token
        }
        return Response(context)


# 找回密码第四步
class FindPasswordFourthAPIView(APIView):
    def post(self,request,user_id):
        data = request.data
        access_token = data['access_token']
        check_user_id = check_access_token_to_user_id(access_token)
        if int(user_id) != check_user_id:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        usr_obj = User.objects.get(id=user_id)
        serializer = PasswordSerializer(instance=usr_obj,data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(status=status.HTTP_200_OK)
