import datetime

from django.db import models

table_names = ['SWP', 'TEMPERATURE', 'PRESSURE', 'HUMIDITY', 'RAINFALL', 'LEAF_WETNESS', 'WIND_DIRECTION', 'WIND_GUST', 'WIND_SPEED']


class Data(models.Model):
    sensor_name = models.CharField(max_length=255, null=False)
    date = models.DateField()
    time = models.TimeField()
    value = models.FloatField(null=True)
    signal = models.CharField(max_length=200)

    objects = models.Manager()

    class Meta:
        managed = False
        abstract = True


class Stats(models.Model):
    sensor_name = models.CharField(max_length=255)
    year = models.IntegerField(default=datetime.date.today().year)
    month = models.SmallIntegerField(default=datetime.date.today().month)
    feature = models.CharField(max_length=255)
    mean = models.FloatField()
    min = models.FloatField()
    max = models.FloatField()


class Sensors(models.Model):
    sensor_name = models.CharField(max_length=255, null=False)
    sensor_id = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.sensor_name


class Swp(Data):
    class Meta:
        db_table = table_names[0]


class Tmp(Data):
    class Meta:
        db_table = table_names[1]


class Prs(Data):
    class Meta:
        db_table = table_names[2]


class Hum(Data):
    class Meta:
        db_table = table_names[3]


class Rnf(Data):
    class Meta:
        db_table = table_names[4]


class Lfw(Data):
    class Meta:
        db_table = table_names[5]


class Wnd(Data):
    class Meta:
        db_table = table_names[6]


class Wng(Data):
    class Meta:
        db_table = table_names[7]


class Wns(Data):
    class Meta:
        db_table = table_names[8]

