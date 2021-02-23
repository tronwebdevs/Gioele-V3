# Generated by Django 3.1.6 on 2021-02-23 13:24

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('api', '0002_banneduser_stat'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('item', models.CharField(max_length=4)),
                ('price', models.FloatField()),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('by', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.guser')),
            ],
        ),
    ]
