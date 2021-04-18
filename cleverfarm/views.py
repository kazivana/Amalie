import csv
import json
from django.core.serializers.json import DjangoJSONEncoder
from django.http import HttpResponseNotAllowed, JsonResponse
from django.shortcuts import render, HttpResponse
from django.utils import timezone
from .models import *
from .forms import Select, Save, SaveDyn, SelectChart


tables = [Swp, Tmp, Hum, Prs, Rnf, Lfw, Wns, Wng, Wnd]


def select_data(req):
    if req.method == 'POST':
        select = Select(req.POST)
        if select.is_valid():
            cd = select.cleaned_data
            data = []
            choices = []
            for table in tables:
                if cd['sensor_name'] == 'all':
                    single = table.objects.filter(date__gt=cd['date_from'], date__lt=cd['date_to']).using('cleverfarm')
                    data.append({'name': table.__name__, 'data': list(single.values())})
                else:
                    single = table.objects.filter(sensor_name=cd['sensor_name'], date__gt=cd['date_from'], date__lt=cd['date_to']).using('cleverfarm')
                    data.append({'name': table.__name__, 'data': list(single.values())})
            for rec in data:
                if rec['data']:
                    choices.append((rec['name'], rec['name']))
            save = SaveDyn(choices)
            selch = SelectChart()
            req.session['data'] = json.dumps(data, cls=DjangoJSONEncoder)
            return render(req, '../templates/dashboard/tabs.html', {'data': data, 'save': save, 'selch': selch})
    else:
        select = Select()
        return render(req, '../templates/dashboard/select.html', {'select': select})


def save_data(req):
    if req.method == 'POST':
        save = Save(req.POST)
        if save.is_valid():
            cd = save.cleaned_data
            if cd['format'] == 'csv':
                data = json.loads(req.session.get('data'))
                res = HttpResponse(content_type='text/csv')
                res['Content-Disposition'] = 'attachment; filename="%s_%s.csv"' % (cd['table'], timezone.now())
                writer = csv.writer(res)
                writer.writerow(['id', 'sensor_name', 'date', 'time', 'value'])
                for table in data:
                    if table['name'] == cd['table']:
                        if table['data']:
                            for row in table['data']:
                                writer.writerow(row.values())
            elif cd['format'] == 'json':
                data = json.loads(req.session.get('data'))
                for table in data:
                    if table['name'] == cd['table']:
                        if table['data']:
                            save_dt = json.dumps(table)
                            res = HttpResponse(save_dt, content_type='application/json')
                            res['Content-Disposition'] = 'attachment; filename="%s_%s.json"' % (cd['table'], timezone.now())
            return res


def line_chart(req):
    data = json.loads(req.session.get('data'))
    labels = []
    body = []
    for table in data:
        if table.data:
            labels.append(table['name'])
            body.append(table['data']['value'])
    print(body)
    res = JsonResponse(data={
        'labels':labels,
        'data':body,
    }, safe=False)
    return res
