# Generated by Django 3.1.5 on 2021-01-30 13:51

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0005_auto_20210130_1344'),
    ]

    operations = [
        migrations.AlterField(
            model_name='guser',
            name='auth',
            field=models.BooleanField(default=False, verbose_name='Email authentication completed'),
        ),
    ]
