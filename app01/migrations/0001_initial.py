# Generated by Django 5.0.2 on 2024-03-03 10:10

import app01.models
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = []

    operations = [
        migrations.CreateModel(
            name="UserProfile",
            fields=[
                (
                    "username",
                    models.CharField(
                        max_length=11,
                        primary_key=True,
                        serialize=False,
                        verbose_name="用户名",
                    ),
                ),
                ("nickname", models.CharField(max_length=32, verbose_name="昵称")),
                ("password", models.CharField(max_length=32, verbose_name="密码")),
                ("email", models.EmailField(max_length=254)),
                ("phone", models.CharField(max_length=32, verbose_name="手机号")),
                ("avatar", models.ImageField(null=True, upload_to="avatar")),
                (
                    "sign",
                    models.CharField(
                        default=app01.models.de_sign, max_length=50, verbose_name="签名"
                    ),
                ),
                (
                    "info",
                    models.CharField(default="", max_length=150, verbose_name="个人信息"),
                ),
                (
                    "create_time",
                    models.DateTimeField(auto_now_add=True, verbose_name=""),
                ),
                ("update_time", models.DateTimeField(auto_now=True)),
            ],
            options={
                "db_table": "user_user_profile",
            },
        ),
    ]
