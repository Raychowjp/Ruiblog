from django.core.cache import cache

from .logging_dec import get_user_by_request

def cache_set(expire):
    def _cache_set(func):
        def wrapper(request, *args, **kwargs):

            if 't_id' in request.GET:
                #当前请求是获取文章详情页
                return func(request, *args, **kwargs)
            visitor_user = get_user_by_request(request)
            visitor_username = None
            if visitor_user:
                visitor_username = visitor_user.username
            author_username = kwargs['author_id']
            full_path = request.get_full_path()
            if visitor_username == author_username:
                cache_key = 'topics_cache_self_%s'%(full_path)
            else:
                cache_key = 'topics_cache_%s'%(full_path)

            #判断是否已经有缓存
            res = cache.get(cache_key)
            if res:
                return res
            #没缓存，执行视图函数
            res = func(request, *args, **kwargs)
            #存储缓存
            cache.set(cache_key, res, expire)

            return res
        return wrapper
    return _cache_set
