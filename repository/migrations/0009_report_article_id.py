# Generated by Django 2.0.5 on 2018-08-12 02:02

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('repository', '0008_report'),
    ]

    operations = [
        migrations.AddField(
            model_name='report',
            name='article_id',
            field=models.ForeignKey(default=0, on_delete=django.db.models.deletion.CASCADE, related_name='a', to='repository.Article'),
        ),
    ]