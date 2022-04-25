from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from django.http import Http404
from .models import Destination , Hotel, Trip
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime, timedelta, date
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


class trip_list_by_destination(LoginRequiredMixin, ListView):
    model = Trip
    # template_name = 'reservation/hotel/hotel_list.html'
    template_name = 'reservation/trip/trip_list_by_destination.html'

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

class trip_list(LoginRequiredMixin, ListView):
    model = Trip
    # template_name = 'reservation/hotel/hotel_list.html'
    template_name = 'reservation/trip/trip_list.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['time'] = self.kwargs.get("time")
        if self.kwargs.get("time") == 'upcoming':
            context['object_list'] = Trip.objects.filter(
                date_from__gte=date.today())
        elif self.kwargs.get("time") == 'previous':
            context['object_list'] = Trip.objects.filter(
                date_until__lt=date.today())
        elif self.kwargs.get("time") == 'ongoing':
            context['object_list'] = Trip.objects.filter(
                date_from__lte=date.today(), date_until__gte=date.today())
        else:
            context['object_list'] = Trip.objects.all()
        return context
class trip_list_by_hotel(LoginRequiredMixin, ListView):
    model = Trip
    # template_name = 'reservation/hotel/hotel_list.html'
    template_name = 'reservation/trip/trip_list_by_hotel.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        hotel = Hotel.objects.get(slug=self.kwargs.get("slug"))
        context['hotel'] = hotel
        context['destination'] = hotel.destination
        context['time'] = self.kwargs.get("time")
        print(self.kwargs.get("time"))
        if self.kwargs.get("time") == 'upcoming':
            print('upcoming')
            context['object_list'] = Trip.objects.filter(
                accommodation=hotel, date_from__gte=timezone.now())
        elif self.kwargs.get("time") == 'previous':
            context['object_list'] = Trip.objects.filter(
                accommodation=hotel, date_until__lt=timezone.now())
        elif self.kwargs.get("time") == 'ongoing':
            print('ongoing')
            context['object_list'] = Trip.objects.filter(
                accommodation=hotel, date_from__lte=timezone.now(), date_until__gte=timezone.now())
        else:
            context['object_list'] = Trip.objects.filter(
                accommodation=hotel)
        return context
class trip_detail(LoginRequiredMixin, DetailView):
    model = Trip
    template_name = 'reservation/trip/trip_detail.html'

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        context['hotel'] = self.get_object().accommodation
        
        return context


class trip_delete(DeleteView):
    model = Trip
    template_name = "reservation/confirm_delete.html"
    success_url = reverse_lazy('reservation:trip_list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(trip_delete, self).get_object()
        if not obj.creation_user == self.request.user:
            raise Http404
        return obj
    
