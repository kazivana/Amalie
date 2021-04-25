from django.urls import path
from . import views


app_name = 'cleverfarm'

urlpatterns = [
    path('select/', views.select_data, name='select_data'),
    path('save/', views.save_data, name='save_data'),
    path('line_chart/', views.line_chart, name='line_chart'),

]
