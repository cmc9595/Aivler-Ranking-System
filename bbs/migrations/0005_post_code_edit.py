# Generated by Django 4.0.1 on 2022-01-26 01:01

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0004_post_views'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='code_edit',
            field=models.TextField(blank=True),
        ),
    ]