from django.shortcuts import render
from reservation.models import Client
from django.shortcuts import get_object_or_404
from django.db.models import Avg, Count, Min, Sum
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
import csv

from django.http import HttpResponse
# Create your views here.


class client_list(LoginRequiredMixin, ListView):
    model = Client
    template_name = 'client/list.html'
    paginate_by = 20
    def get_queryset(self):
        query = self.request.GET.get('query')
        if query:
            qs = Client.objects.filter(phone__icontains=query)
        else:
            qs = Client.objects.all()    
        return qs

class client_detail(LoginRequiredMixin, DetailView):
    model = Client
    template_name = 'client/detail.html'
    

def export_clients_csv(request):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="clients.csv"'

    writer = csv.writer(response)
    writer.writerow(['name', 'phone', 'phone2'])

    clients = Client.objects.all().values_list(
        'name', 'phone', 'phone2')
    for client in clients:
        writer.writerow(client)
    return response
