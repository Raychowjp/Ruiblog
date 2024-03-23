import json

from django.views import View
from django.http import JsonResponse
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.core.cache import cache
from app01.models import UserProfile
from message.models import Message
from tools.cache_dec import cache_set
from tools.logging_dec import logging_check, get_user_by_request
from topic.models import Topic


#异常码：10300-10399
# Create your views here.
class TopicViews(View):

    def clear_topics_caches(self, request):
        path = request.path_info
        cache_key_p = ['topics_cache_self_','topics_cache_'] #前缀
        cache_key_h = ['', '?category = tec', '?category = no-tec'] #后缀
        all_keys = []#所有可能性
        for key_p in cache_key_p:
            for key_h in cache_key_h:
                all_keys.append(key_p + path + key_h)
        cache.delete_many(all_keys)

    def make_topic_res(self, author, author_topic, is_self):
        if is_self:
            #自己访问自己的博客
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author).first()#id__gt:isGreaterThan
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author).last()
        else:
            #访客访问
            next_topic = Topic.objects.filter(id__gt=author_topic.id, author=author,limit='public').first()  # id_gt:isGreaterThan
            last_topic = Topic.objects.filter(id__lt=author_topic.id, author=author,limit='public').last()

        next_id = next_topic.id if next_topic else None
        next_title = next_topic.title if next_topic else ''
        last_id = last_topic.id if last_topic else None
        last_title = last_topic.title if last_topic else ''
        #处理留言
        all_messages = Message.objects.filter(topic=author_topic).order_by('-created_time')
        msg_list = []
        rep_dic = {}
        m_count = 0
        for msg in all_messages:
            if msg.parent_message:
                rep_dic.setdefault(msg.parent_message,[])#setdefault意思是有这个key就不管，没有就生成key，值是[]
                rep_dic[msg.parent_message].append({'msg_id':msg.id, 'publisher':msg.publisher.nickname, 'publisher_avatar':str(msg.publisher.avatar), 'content':msg.content,
                                                    'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S')})
            else:
                m_count += 1
                msg_list.append({'id':msg.id, 'publisher':msg.publisher.nickname, 'publisher_avatar':str(msg.publisher.avatar), 'content':msg.content,
                                                    'created_time':msg.created_time.strftime('%Y-%m-%d %H:%M:%S'),'reply':[]})
        print(rep_dic)
        for m in msg_list:
            if m['id'] in rep_dic:
                m['reply'] = rep_dic[m['id']]


        res = {'code':200, 'data':{}}
        res['data']['nickname'] = author.nickname
        res['data']['title'] = author_topic.title
        res['data']['category'] = author_topic.category
        res['data']['created_time'] = author_topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
        res['data']['content'] = author_topic.content
        res['data']['introduce'] = author_topic.introduce
        res['data']['author'] = author.nickname
        res['data']['last_id'] = last_id
        res['data']['last_title'] = last_title
        res['data']['next_id'] = next_id
        res['data']['next_title'] = next_title
        res['data']['messages'] = [msg_list]
        print(res['data']['messages'])

        res['data']['messages_count'] = m_count
        return res


    def make_topics_res(self, author, author_topics):
        #获取文章内容，按照前端要求的字典返回
        res = {'code':200, 'data':{}}
        topics_res = []
        #循环这个queryset，取到所有的文章
        for topic in author_topics:
            d = {}
            d['id'] = topic.id
            d['title'] = topic.title
            d['category'] = topic.category
            d['created_time'] = topic.created_time.strftime('%Y-%m-%d %H:%M:%S')
            d['introduce'] = topic.introduce
            d['author'] = topic.author.nickname
            topics_res.append(d)
        res['data']['topics'] = topics_res
        res['data']['nickname'] = author.nickname
        return res

        return {'code':200, }

    @method_decorator(logging_check)
    def post(self, request, author_id):
        author= request.myuser #装饰器里拿到user
        json_str = request.body
        json_obj = json.loads(json_str)
        title = json_obj['title']
        content = json_obj['content']
        content_text = json_obj['content_text']
        introduce = content_text[:30]
        limit = json_obj['limit']
        category = json_obj['category']
        if limit not in ['public','private ']:
            result = {'code':10300, 'error':'Limit error'}
            return JsonResponse(result)
        #创建topic数据
        Topic.objects.create(title=title, content=content, limit=limit, introduce=introduce, category=category, author=author)
        #删除cache
        self.clear_topics_caches(request)
        return JsonResponse({'code':200})



    @method_decorator(cache_set(300))
    def get(self, request, author_id):
        #这里需要分两种情况：本人访问自己的博客，他人访问自己的博客
        try:
            author = UserProfile.objects.get(username = author_id)
        except Exception as e:
            result = {'code': 10301, 'error':'AUthor does not exist'}
            return JsonResponse(result)
        visitor = get_user_by_request(request)
        visitor_username = None
        if visitor is not None:
            visitor_username = visitor.username

        #获取指定某id的文章数据
        t_id = request.GET.get('t_id')
        if t_id:
            t_id = int(t_id)
            is_self = False
            if visitor_username == author_id:
                is_self = True
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=author_id)
                except Exception as e:
                    result = {'code':10302, 'error':'No topic'}
                    return JsonResponse(result)
            else:
                try:
                    author_topic = Topic.objects.get(id=t_id, author_id=author_id, limit='public')
                except Exception as e:
                    result = {'code': 10303, 'error': 'No topic'}
                    return JsonResponse(result)

            res = self.make_topic_res(author, author_topic, is_self)
            return JsonResponse(res)
        else:
            #没有指定id就获取整个列表页
            #是否有查询某个category(tec/no-tec)
            category = request.GET.get('category')
            if category is not None:
                #自己访问自己
                if visitor_username == author_id:
                    author_topics = Topic.objects.filter(author_id = author_id, category = category)
                else:
                    author_topics = Topic.objects.filter(author_id = author_id, limit='public', category=category)
            else:
                if visitor_username == author_id:
                    author_topics = Topic.objects.filter(author_id = author_id)
                else:
                    author_topics = Topic.objects.filter(author_id = author_id, limit='public')
            res = self.make_topics_res(author, author_topics)
            return JsonResponse(res)

    def delete(self,request,author_id):
        delete_id = int(request.GET.get('t_id'))
        print(delete_id)
        if delete_id is not None:
            delete_topic = Topic.objects.get(id=delete_id)
            delete_topic.delete()
            self.clear_topics_caches(request)
            return JsonResponse({'code':200})
        else:
            result = {'code': 10304, 'error': 'No such topic'}
            return JsonResponse(result)



