from django.db import models



class Data(models.Model):
    sensor_name = models.CharField(max_length=255, null=False)
    date = models.DateField()
    time = models.TimeField()
    value = models.FloatField(null=True)

    objects = models.Manager()

    class Meta:
        managed = False
        abstract = True


class Sensors(models.Model):
    sensor_name = models.CharField(max_length=255, null=False)
    sensor_id = models.CharField(max_length=255, null=False)

    def __str__(self):
        return self.sensor_name


class Swp(Data):
    class Meta:
        db_table = 'swp'


class Tmp(Data):
    class Meta:
        db_table = 'tmp'


class Prs(Data):
    class Meta:
        db_table = 'prs'


class Hum(Data):
    class Meta:
        db_table = 'hum'


class Rnf(Data):
    class Meta:
        db_table = 'rnf'


class Lfw(Data):
    class Meta:
        db_table = 'lfw'


class Wns(Data):
    class Meta:
        db_table = 'wns'


class Wng(Data):
    class Meta:
        db_table = 'wng'


class Wnd(Data):
    class Meta:
        db_table = 'wnd'

