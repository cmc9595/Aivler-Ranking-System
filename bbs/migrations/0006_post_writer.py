# Generated by Django 3.2.5 on 2022-01-26 16:20

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('bbs', '0005_post_code_edit'),
    ]

    operations = [
        migrations.AddField(
            model_name='post',
            name='writer',
            field=models.CharField(blank=True, max_length=150),
        ),
    ]