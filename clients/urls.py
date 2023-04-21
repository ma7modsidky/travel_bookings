from django.urls import path, include
from . import views

app_name= 'clients'

urlpatterns = [
    path('client_list',
         views.client_list.as_view(), name='client_list'),
    path('client/<int:pk>',
         views.client_detail.as_view(), name='client_detail'),
    path('export_csv',
         views.export_clients_csv, name='client_export_csv'),
]