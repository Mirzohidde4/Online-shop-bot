# Generated by Django 5.1.2 on 2025-02-05 11:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='basketmod',
            name='created_at',
            field=models.DateTimeField(auto_now_add=True, null=True, verbose_name='sana'),
        ),
    ]
