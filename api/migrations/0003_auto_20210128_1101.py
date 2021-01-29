# Generated by Django 3.1.5 on 2021-01-28 11:01

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
        ('api', '0002_auto_20210127_1815'),
    ]

    operations = [
        migrations.DeleteModel(
            name='GUser',
        ),
        migrations.AlterField(
            model_name='visitor',
            name='referrer',
            field=models.CharField(max_length=512, null=True),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='screen_height',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='screen_width',
            field=models.IntegerField(default=-1),
        ),
        migrations.AlterField(
            model_name='visitor',
            name='visit_time',
            field=models.DateTimeField(auto_now_add=True),
        ),
        migrations.CreateModel(
            name='GUser',
            fields=[
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, primary_key=True, serialize=False, to='auth.user')),
                ('auth', models.BooleanField(default=False)),
                ('score', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Gioele User',
            },
        ),
        migrations.AlterField(
            model_name='Game',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.guser'),
        ),
        migrations.AlterField(
            model_name='game',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='api.guser'),
        ),
    ]
