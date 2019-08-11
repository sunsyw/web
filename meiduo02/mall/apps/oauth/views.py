from django.shortcuts import render

# Create your views here.
from rest_framework.views import APIView
from QQLoginTool.QQtool import OAuthQQ
from mall import settings
from rest_framework.response import Response
from rest_framework import status
from oauth.models import OAuthQQUser
from oauth.utils import jwt_login
from oauth.utils import generate_openid_token
from oauth.serializers import OauthQQUserSerializer

class QQAuthURLAPIView(APIView):
    def get(self,request):
        state = request.query_params.get('state')
        if not state:
            state = '/'

        # 获取qq登录网址
        oauth = OAuthQQ(client_id=settings.QQ_CLIENT_ID,
                        client_secret=settings.QQ_CLIENT_SECRET,
                        redirect_uri=settings.QQ_REDIRECT_URI,
                        state=state)
        auth_url = oauth.get_qq_url()

        return Response({'auth_url':auth_url})

class OauthQQUserAPIView(APIView):
    def get(self,request):
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
            return Response({'access_token':openid_itsdangerous})
        else:
            # 没有异常则登录
            # 登录状态token
            token = jwt_login(qquser)
            return Response({'token':token,
                             'username':qquser.user.username,
                             'user_id':qquser.user.id})


    def post(self,request):
        data = request.data
        serializer = OauthQQUserSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        qquser = serializer.save()
        # 自动登录
        token = jwt_login(qquser)
        return Response({'token':token,
                         'username':qquser.user.username,
                         'user_id':qquser.user.id})

