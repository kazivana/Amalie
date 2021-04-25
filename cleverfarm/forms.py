from django import forms
from django.urls import reverse

SENSORS = [
    ("all", '---All---'),
    ("BP I/1 puda10", 'BP I/1 puda10'),
    ("BP I/1 puda20", 'BP I/1 puda20'),
    ("BP I/2 puda10", 'BP I/2 puda10'),
    ("BP I/2 puda20", 'BP I/2 puda20'),
    ("BP I/1-mikroklima", 'BP I/1-mikroklima'),
    ("Meteo Plus", 'Meteo Plus'),
    ]


formats = [
    ('csv','CSV'),
    ('json','JSON'),
]



class Select(forms.Form):
    sensor_name = forms.CharField(label='Sensor name', widget=forms.Select(choices=SENSORS), required=False)
    date_from = forms.DateField(widget= forms.SelectDateWidget)
    date_to = forms.DateField(widget= forms.SelectDateWidget)


class SaveDyn(forms.Form):
    def __init__(self, better_choices, *args, **kwargs):
        super(SaveDyn, self).__init__(*args, **kwargs)
        self.fields['table'].choices = better_choices
    table = forms.ChoiceField(choices=(), required=False)
    format = forms.CharField(label='Format', widget=forms.Select(choices=formats), required=False)


class Save(forms.Form):
    table = forms.CharField(max_length=3, required=False)
    format = forms.CharField(label='Format', widget=forms.Select(choices=formats), required=False)


class SelectChart(forms.Form):
    type = forms.CharField(label='Plot type', widget=forms.Select(choices=[('line','Line')]), required=False)