import json
import random
from django.core.cache import cache
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views import View
from .models import UserProfile
import hashlib
from tools.logging_dec import logging_check
from tools.sms import YunTongXin
from .tasks import send_sms_c
#异常码 10100 - 10199


# Create your views here.
#FBV
@logging_check
def users_views(request, username):

    if request.method != 'POST':
        result = {'code':10103, 'error':'Please use POST'}
        return JsonResponse(result)
    user = request.myuser
    avatar = request.FILES['avatar']
    user.avatar = avatar
    user.save()
    return JsonResponse({'code':200})
#CBV
#更灵活[可继承]
#对未定义的http method请求 直接返回405响应
class UserViews(View):

    def get(self, request, username=None):
        if username:
            print(username)
            try:
                user = UserProfile.objects.get(username=username)
            except Exception as e:
                result ={'code':10102, 'error':'the username does not exist'}
                print(e)
                return JsonResponse(result)
            result = {'code':200, 'username':username, 'data':{'info':user.info, 'sign':user.sign, 'nickname':user.nickname,'avatar':str(user.avatar)}}
            return JsonResponse(result)
        else:
            pass

    #
        return JsonResponse({'code':200,'msg':'test'})

    def post(self, request):

        json_str = request.body
        json_obj = json.loads(json_str)
        username = json_obj['username']
        email = json_obj['email']
        password_1 = json_obj['password_1']
        password_2 = json_obj['password_2']
        phone = json_obj['phone']
        sms_num = json_obj['sms_num']

        if password_1 != password_2:
            result = {'code':10100, 'error':'The two passwords do not match'}
            return JsonResponse(result)

        old_code = cache.get('sms_%s'%(phone))
        if not old_code:
            result = {'code':10110, 'error':"验证码过期"}
            return JsonResponse(result)
        if int(sms_num) != old_code:
            result = {'code': 10111, 'error': "验证码错误"}
            return JsonResponse(result)


        #参数基本检查
        #检查用户名是否可用
        old_user = UserProfile.objects.filter(username=username)
        if old_user:
            result  = {'code':10101, 'error':'The username is already existed'}
            return JsonResponse(result)

        #UserProfile插入数据(密码md5存储)

        p_m = hashlib.md5()
        p_m.update(password_1.encode())

        #开始创建数据
        UserProfile.objects.create(username=username, nickname=username, email=email, password=p_m.hexdigest(), phone=phone)



        result = {'code':200, 'username':username, 'data':{}}
        response = JsonResponse(result)
        response['Access-Control-Allow-Origin'] = 'http://localhost:63342'
        return response
    @method_decorator(logging_check)
    def put(self, request, username=None):#更新用户数据,一查二改三更新
        json_str = request.body
        json_obj = json.loads(json_str)
        user = request.myuser
        user.sign = json_obj['sign']
        user.info = json_obj['info']
        user.nickname = json_obj['nickname']

        user.save()
        return JsonResponse({'code':200})

def sms_view(request):
    if request.method != 'POST':
        result = {'code':10108, 'error':'Please use post method'}
        return JsonResponse(result)

    json_str = request.body
    json_obj = json.loads(json_str)
    phone = json_obj['phone']
    code = random.randint(1000, 9999)
    #存储验证码 django_redis
    cache_key = 'sms_%d' %(int(phone))
    #检查是否已经有有效期内的验证码
    old_code = cache.get(cache_key)
    if old_code:
        result = {'code': 10111, 'error': '验证码已经被发送'}
        return JsonResponse(result)
    cache.set(cache_key, code, 60)
    #send_sms(phone,code)
    #celery版本发送:即使第三方平台（容联云）阻塞，并不会影响django，仍然可以迅速返回响应
    send_sms_c(phone,code)
    return JsonResponse({'code':200, })

def send_sms(phone,code):
    config = {
        'accountSid': '2c94811c8cd4da0a018e3ca4d07a3971',
        'accountToken': '0d91d04940684cdb947de694a04fc166',
        'appId': '2c94811c8cd4da0a018e3ca4d2133978',
        'templateId': '1'
    }
    yun = YunTongXin(**config)
    res = yun.run(phone, code)
    print(res)










