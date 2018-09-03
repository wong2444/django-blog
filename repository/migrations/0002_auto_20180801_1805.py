# Generated by Django 2.0.5 on 2018-08-01 18:05

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='comment',
            name='create_time',
            field=models.DateTimeField(default=django.utils.timezone.now, verbose_name='创建时间'),
        ),
        migrations.AlterField(
            model_name='userinfo',
            name='avatar',
            field=models.ImageField(default='static/imgs/avatar/default.png', upload_to='./static/imgs/avatar/', verbose_name='头像'),
        ),
    ]