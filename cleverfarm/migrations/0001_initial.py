# Generated by Django 3.1.7 on 2021-04-14 12:16

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Hum',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'hum',
            },
        ),
        migrations.CreateModel(
            name='Lfw',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'lfw',
            },
        ),
        migrations.CreateModel(
            name='Prs',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'prs',
            },
        ),
        migrations.CreateModel(
            name='Rnf',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'rnf',
            },
        ),
        migrations.CreateModel(
            name='Sensors',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('sensor_id', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='Swp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'swp',
            },
        ),
        migrations.CreateModel(
            name='Tmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'tmp',
            },
        ),
        migrations.CreateModel(
            name='Wnd',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'wnd',
            },
        ),
        migrations.CreateModel(
            name='Wng',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'wng',
            },
        ),
        migrations.CreateModel(
            name='Wns',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('sensor_name', models.CharField(max_length=255)),
                ('date', models.DateField()),
                ('time', models.TimeField()),
                ('value', models.FloatField(null=True)),
            ],
            options={
                'db_table': 'wns',
            },
        ),
    ]