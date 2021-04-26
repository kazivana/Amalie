# Generated by Django 3.1.7 on 2021-04-25 12:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('cleverfarm', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Stats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('year', models.IntegerField(default=2021)),
                ('month', models.SmallIntegerField(default=4)),
                ('feature', models.CharField(max_length=255)),
                ('mean', models.FloatField()),
                ('min', models.FloatField()),
                ('max', models.FloatField()),
            ],
        ),
    ]