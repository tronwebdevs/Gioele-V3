# Generated by Django 3.1.7 on 2021-03-07 13:48

import api.utils
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Ability',
            fields=[
                ('id', models.CharField(default=api.utils.generate_short_id, editable=False, max_length=4, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=128)),
                ('price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='BulletPattern',
            fields=[
                ('id', models.CharField(default=api.utils.generate_short_id, editable=False, max_length=4, primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=128)),
                ('function', models.CharField(max_length=1024)),
                ('behavior', models.CharField(default=None, max_length=1024, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='GUser',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, related_name='user', serialize=False, to='auth.user')),
                ('auth', models.BooleanField(default=False, verbose_name='Email authentication completed')),
                ('level', models.FloatField(default=0)),
                ('balance', models.FloatField(default=0)),
                ('skin', models.CharField(max_length=4)),
                ('main_gun', models.CharField(max_length=4)),
                ('side_gun', models.CharField(default=None, max_length=4, null=True)),
            ],
            options={
                'verbose_name': 'Gioele User',
            },
        ),
        migrations.CreateModel(
            name='Skin',
            fields=[
                ('id', models.CharField(default=api.utils.generate_short_id, editable=False, max_length=4, primary_key=True, serialize=False)),
                ('description', models.CharField(max_length=256)),
                ('name', models.CharField(max_length=128)),
                ('price', models.FloatField()),
            ],
        ),
        migrations.CreateModel(
            name='Stat',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('key', models.CharField(max_length=16)),
                ('value', models.FloatField()),
                ('at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='UserInventory',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('main_guns', models.CharField(default=None, max_length=256, null=True)),
                ('side_guns', models.CharField(default=None, max_length=256, null=True)),
                ('skins', models.CharField(default=None, max_length=256, null=True)),
                ('abilities', models.CharField(default=None, max_length=256, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='VisitLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('ip', models.CharField(max_length=16)),
                ('platform', models.CharField(max_length=128)),
                ('lang', models.CharField(max_length=6)),
                ('browser', models.CharField(max_length=256)),
                ('screen_width', models.IntegerField()),
                ('screen_height', models.IntegerField()),
                ('referrer', models.CharField(max_length=512, null=True)),
                ('has_touchscreen', models.BooleanField(default=False)),
                ('has_ad_blocker', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('updated_at', models.DateTimeField(auto_now_add=True)),
            ],
        ),
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
        migrations.CreateModel(
            name='LoginLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('timestamp', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.guser')),
                ('visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.visitlog')),
            ],
        ),
        migrations.AddField(
            model_name='guser',
            name='inventory',
            field=models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='inventory', to='api.userinventory'),
        ),
        migrations.CreateModel(
            name='Gun',
            fields=[
                ('id', models.CharField(default=api.utils.generate_short_id, editable=False, max_length=4, primary_key=True, serialize=False)),
                ('type', models.SmallIntegerField(choices=[(0, 'main'), (1, 'side')])),
                ('price', models.FloatField()),
                ('name', models.CharField(max_length=128)),
                ('description', models.CharField(max_length=256)),
                ('cooldown', models.IntegerField()),
                ('damage', models.IntegerField()),
                ('shoot', models.CharField(max_length=1024)),
                ('pattern', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to='api.bulletpattern')),
            ],
        ),
        migrations.CreateModel(
            name='GameLog',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False)),
                ('time_start', models.DateTimeField()),
                ('time_end', models.DateTimeField()),
                ('exp_gained', models.IntegerField()),
                ('gbucks_earned', models.IntegerField()),
                ('shooted_main', models.IntegerField()),
                ('shooted_main_hit', models.IntegerField()),
                ('shooted_side', models.IntegerField()),
                ('shooted_side_hit', models.IntegerField()),
                ('killed', models.CharField(max_length=256)),
                ('powerups', models.CharField(max_length=256)),
                ('abilities', models.CharField(max_length=256)),
                ('skin', models.CharField(max_length=4)),
                ('main_gun', models.CharField(max_length=4)),
                ('side_gun', models.CharField(default=None, max_length=4, null=True)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.guser')),
                ('visit', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.visitlog')),
            ],
        ),
        migrations.CreateModel(
            name='BannedUser',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('reason', models.CharField(max_length=256)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='by', to=settings.AUTH_USER_MODEL)),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='api.guser')),
            ],
        ),
        migrations.CreateModel(
            name='AdminLog',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('action', models.CharField(max_length=256)),
                ('datetime', models.DateTimeField(auto_now_add=True)),
                ('by', models.ForeignKey(null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
