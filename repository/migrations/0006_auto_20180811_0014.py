# Generated by Django 2.0.5 on 2018-08-11 00:14

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0005_permission_pattern'),
    ]

    operations = [
        migrations.AlterField(
            model_name='permission',
            name='pattern',
            field=models.BooleanField(default=True),
        ),
    ]