# Generated by Django 5.1.2 on 2025-01-21 12:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0012_alter_basketmod_category'),
    ]

    operations = [
        migrations.AddField(
            model_name='usermod',
            name='phone',
            field=models.CharField(default=2, max_length=20, verbose_name='tel raqam'),
            preserve_default=False,
        ),
        migrations.AlterField(
            model_name='basketmod',
            name='category',
            field=models.PositiveIntegerField(verbose_name='kategoriya id'),
        ),
    ]
