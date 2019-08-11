from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from mall import settings
from rest_framework.response import Response
from rest_framework import status
from oauth.models import OAuthQQUser, OAuthSinaUser
from oauth.utils import jwt_login, generate_access_token
from oauth.utils import generate_openid_token
from oauth.serializers import OauthQQUserSerializer, OauthSinaUserSerializer

# 提供QQ登录页面网址
from oauth.weibo import OAuthWeibo


class QQAuthURLAPIView(APIView):
    def get(self, request):
        state = request.query_params.get('state')
        if not state:
            state = '/'

        # 获取qq登录网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)
        auth_url = oauth.get_qq_url()

        return Response({'auth_url': auth_url})


# 用户扫码登录的回调处理
class OauthQQUserAPIView(APIView):
    def get(self, request):
        # 接收code
        code = request.query_params.get('code')
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 用code换取token
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI)
        try:
            token = oauth.get_access_token(code)
            # 通过token换取openid
            openid = oauth.get_open_id(token)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        # 通过openid查询判断
        try:
            qquser = OAuthQQUser.objects.get(openid=openid)
        except OAuthQQUser.DoesNotExist:
            # 如果没有查询出来，则创建用户
            openid_itsdangerous = generate_openid_token(openid)
            return Response({'access_token': openid_itsdangerous})
        else:
            # 没有异常则登录
            # 登录状态token
            token = jwt_login(qquser)
            return Response({'token': token,
                             'username': qquser.user.username,
                             'user_id': qquser.user.id})

    # openid绑定到用户
    def post(self, request):
        data = request.data
        serializer = OauthQQUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        qquser = serializer.save()
        # 自动登录
        token = jwt_login(qquser)
        return Response({'token': token,
                         'username': qquser.user.username,
                         'user_id': qquser.user.id})


class WeiboAuthURLLView(APIView):

    def get(self, request):
        # 获取微博登录的链接
        next = request.query_params.get('state')
        if not next:
            next = "/"

        # 获取微博登录网页
        oauth = OAuthWeibo(client_id=settings.WEIBO_CLIENT_ID,
                           client_secret=settings.WEIBO_CLIENT_SECRET,
                           redirect_uri=settings.WEIBO_REDIRECT_URI,
                           state=next)
        login_url = oauth.get_weibo_url()
        return Response({"login_url": login_url})


class WeiboOauthView(APIView):
    def get(self, request):
        # 获取code
        code = request.query_params.get("code")
        if code is None:
            return Response(status=status.HTTP_400_BAD_REQUEST)
        # 通过code获取token值
        oauth = OAuthWeibo(client_id=settings.WEIBO_CLIENT_ID,
                           client_secret=settings.WEIBO_CLIENT_SECRET,
                           redirect_uri=settings.WEIBO_REDIRECT_URI,
                           state=next)
        try:
            access_token = oauth.get_access_token(code)
        except Exception as e:
            return Response(status=status.HTTP_400_BAD_REQUEST)

        try:
            weibo_user = OAuthSinaUser.objects.get(access_token=access_token)
        except OAuthSinaUser.DoesNotExist:
            access_token_itsdangerous = generate_access_token(access_token)
            return Response({'access_token': access_token_itsdangerous})
        else:
            token = jwt_login(weibo_user)

            return Response({
                    'token': token,
                    'username': weibo_user.user.username,
                    'user_id': weibo_user.user.id})

        # openid绑定到用户
    def post(self, request):
        data = request.data
        serializer = OauthSinaUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        sinauser = serializer.save()
        # 自动登录
        token = jwt_login(sinauser)
        return Response({'token': token,
                         'username': sinauser.user.username,
                         'user_id': sinauser.user.id})