# Generated by Django 5.1.2 on 2025-02-09 08:54

import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0002_basketmod_created_at'),
    ]

    operations = [
        migrations.CreateModel(
            name='OrderMod',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('product_name', models.CharField(max_length=100, verbose_name='mahsulot nomi')),
                ('product_price', models.PositiveIntegerField(verbose_name='mahsulot narxi')),
                ('product_count', models.PositiveIntegerField(verbose_name='mahsulot soni')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='sana')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='main.usermod', verbose_name='foydalanuvchi')),
            ],
            options={
                'verbose_name': 'Buyurtma',
                'verbose_name_plural': 'Buyurtmalar',
            },
        ),
    ]
