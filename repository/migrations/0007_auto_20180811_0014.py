# Generated by Django 2.0.5 on 2018-08-11 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0006_auto_20180811_0014'),
    ]

    operations = [
        migrations.AddField(
            model_name='permission',
            name='status',
            field=models.BooleanField(default=True),
        ),
        migrations.AlterField(
            model_name='permission',
            name='pattern',
            field=models.CharField(default='', max_length=128),
        ),
    ]
