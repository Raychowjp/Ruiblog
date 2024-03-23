from django.db import models
from app01.models import UserProfile


# Create your models here.
class Topic(models.Model):
    title = models.CharField(max_length=50, verbose_name='文章标题')
    category = models.CharField(max_length=50, verbose_name='文章分类')
    limit = models.CharField(max_length=20, verbose_name='权限')
    introduce = models.CharField(max_length=90, verbose_name='文章简介')
    content = models.TextField(verbose_name='文章内容') #TextField可变长度文本存储
    created_time = models.DateTimeField(auto_now_add=True)
    updated_time = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    author = models.ForeignKey(UserProfile,on_delete=models.CASCADE) #作者为外键

