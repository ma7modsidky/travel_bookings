from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Destination
# Create your views here.
def home(request):
    return render(request, 'reservation/home.html', {})


class destination_list(ListView):
    model = Destination
    template_name = 'reservation/destination/destination_list.html'
    paginate_by = 9


class destination_detail(DetailView):
    model = Destination
    template_name = 'reservation/destination/destination_detail.html'
    
    
