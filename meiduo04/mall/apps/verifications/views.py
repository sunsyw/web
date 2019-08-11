from django.http import HttpResponse
from django.shortcuts import render

# Create your views here.

from rest_framework.views import APIView
from rest_framework.response import Response
from libs.captcha.captcha import captcha
from django_redis import get_redis_connection

from libs.yuntongxun.sms import CCP
from users.utils import check_access_token_to_mobile
from verifications.serializers import RegisterSmsSerializer
import random
from celery_tasks.sms.tasks import send_sms_code


# 图片验证码
class RegisterImageCodeAPI(APIView):

    def get(self,request,image_code_id):
        # 1.接收uuid
        # 2.生成验证码
        text,image = captcha.generate_captcha()
        print(text)
        # 3.将验证码保存在redis中
        redis_conn = get_redis_connection('code')
        redis_conn.setex('img'+image_code_id,300,text)
        # 4.返回验证码
        return HttpResponse(image,content_type='image/jpeg')


# 手机验证码
class RegisterSmsCodeAPI(APIView):

    def get(self,request,mobile=None):

        # 1.接收数据
        query_params = request.query_params
        # 2.校验数据
        serializer = RegisterSmsSerializer(data=query_params)
        # 3.生成短信验证码
        sms_code = '%06d' % random.randint(0,999999)
        print(sms_code)
        if mobile is None:
            access_token = request.query_params['access_token']
            mobile = check_access_token_to_mobile(access_token)
        # 4.发送短信
        CCP().send_template_sms(mobile, [sms_code, 5], 1)
        # send_sms_code.delay(mobile,sms_code)
        # 5.保存短信
        redis_conn = get_redis_connection('code')
        redis_conn.setex('sms_'+mobile,5*60,sms_code)
        return Response({'msg':'ok'})

