from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from .models import Destination , Hotel, Trip
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
# Create your views here.
def home(request):
    return render(request, 'reservation/home.html', {})


class destination_list(LoginRequiredMixin,ListView):
    model = Destination
    template_name = 'reservation/destination/destination_list.html'
    paginate_by = 9
    redirect_field_name = 'next'


class destination_detail(LoginRequiredMixin,DetailView,):
    model = Destination
    template_name = 'reservation/destination/destination_detail.html'
    
    
class hotel_list(LoginRequiredMixin, ListView):
    model = Hotel
    # template_name = 'reservation/hotel/hotel_list.html'
    template_name = 'reservation/hotel/hotel_list.html'
    paginate_by = 9

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        destination = Destination.objects.get(slug=self.kwargs.get("slug"))
        context['destination'] = destination
        context['object_list'] = Hotel.objects.filter(
            destination=destination).prefetch_related('destination')
        return context


class hotel_detail(LoginRequiredMixin, DetailView):
    model = Hotel
    template_name = 'reservation/hotel/hotel_detail.html'


class trip_list(LoginRequiredMixin, ListView):
    model = Trip
    # template_name = 'reservation/hotel/hotel_list.html'
    template_name = 'reservation/trip/trip_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        destination = Destination.objects.get(slug=self.kwargs.get("slug"))
        context['destination'] = destination
        context['time'] = self.kwargs.get("time")
        print(self.kwargs.get("time"))
        if self.kwargs.get("time") == 'upcoming':
            print('upcoming')
            context['object_list'] = Trip.objects.filter(
                destination=destination, date_from__gte=timezone.now())
        elif self.kwargs.get("time") == 'previous':
            context['object_list'] = Trip.objects.filter(
                destination=destination, date_until__lt=timezone.now())
        elif self.kwargs.get("time") == 'ongoing':
            print('ongoing')
            context['object_list'] = Trip.objects.filter(
                destination=destination, date_from__lte=timezone.now(), date_until__gte=timezone.now())
        else:
            context['object_list'] = Trip.objects.filter(
                destination=destination)
        return context


class trip_detail(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'reservation/hotel/hotel_detail.html'
