from django.http import JsonResponse
import jwt
from django.conf import settings
from app01.models import UserProfile


def logging_check(func):
    def wrap(request, *args, **kwargs):
        token = request.META.get('HTTP_AUTHORIZATION')
        if not token:
            result = {'code':403, 'error':'Please login'}
            return JsonResponse(result)
    #校验jwt,从请求头里取出，这里可以拿到username
        try:
            res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms=['HS256'])
        except Exception as e:
            print('jwt decode error is %s'%e)
            result = {'code': 403, 'error': 'Please login'}
            return JsonResponse(result)
        username = res['username']
        user = UserProfile.objects.get(username=username)
        request.myuser = user
        return func(request, *args, **kwargs)
    return wrap



def get_user_by_request(request):
    token = request.META.get('HTTP_AUTHORIZATION')
    if not token:
        return None
    try:
        res = jwt.decode(token, settings.JWT_TOKEN_KEY, algorithms = ['HS256'])
    except Exception as e:
        return None
    username = res['username']
    user = UserProfile.objects.get(username=username)
    return user
