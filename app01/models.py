from django.db import models
import random
def de_sign():
    signs = ['来吧兄弟', '奔跑吧兄弟']
    return random.choice(signs)
# Create your models here.
class UserProfile(models.Model):
    username = models.CharField(max_length=11, verbose_name='用户名', primary_key=True)
    nickname = models.CharField(max_length=32, verbose_name='昵称')
    password = models.CharField(max_length=32, verbose_name='密码')
    email = models.EmailField()
    phone = models.CharField(max_length=32, verbose_name='手机号')
    avatar = models.ImageField(upload_to='avatar', null=True)
    sign = models.CharField(max_length=50, verbose_name='签名',default=de_sign)
    info = models.CharField(max_length=150, verbose_name='个人信息',default='')
    create_time = models.DateTimeField(auto_now_add=True, verbose_name='')
    update_time = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'user_user_profile'

