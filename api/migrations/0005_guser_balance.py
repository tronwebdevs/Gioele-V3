# Generated by Django 3.1.5 on 2021-01-29 10:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0004_auto_20210128_1318'),
    ]

    operations = [
        migrations.AddField(
            model_name='guser',
            name='balance',
            field=models.IntegerField(default=0),
        ),
    ]
