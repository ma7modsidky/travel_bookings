
from pyexpat import model
from django.shortcuts import get_object_or_404
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView

from django import http
from .models import Destination, Hotel, Trip, TripBooking
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime, timedelta, date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Div, Field
from crispy_tailwind import layout
from .forms import PayTripBookingForm
from django.utils.translation import gettext_lazy as _
# Create your views here.


def home(request):
    return render(request, 'reservation/home.html', {})


class destination_list(LoginRequiredMixin, ListView):
    model = Destination
    template_name = 'reservation/destination/destination_list.html'
    paginate_by = 9
    redirect_field_name = 'next'


class destination_detail(LoginRequiredMixin, DetailView,):
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
    success_url = reverse_lazy('reservation:trip_list', kwargs={'time': 'all'})

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(trip_delete, self).get_object()
        if not obj.creation_user == self.request.user:
            return http.HttpResponseForbidden("Cannot delete other's trips")
        return obj


class trip_booking_list(LoginRequiredMixin, ListView):
    model = TripBooking
    template_name = 'reservation/booking/trip_booking_list.html'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        trip = Trip.objects.get(id=self.kwargs.get('trip_id'))
        bookings = TripBooking.objects.filter(trip=trip)
        context['trip'] = trip
        context['bookings'] = bookings
        return context
    
class trip_booking_create(LoginRequiredMixin, CreateView):
    model = TripBooking
    fields = ['trip', 'single_room_count', 'double_room_count', 'triple_room_count', 'adults', 'children',
              'extra_seats', 'single_room_persons', 'double_room_persons', 'triple_room_persons', 'name', 'email', 'phone', 'phone2', 'notes']
    template_name = 'reservation/booking/trip_booking_create.html'
    exclude = ['creation_user']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(_('Choose trip'),
            Field('trip', css_class='text-center'),
            Fieldset(_('Numbre of Rooms'),
                     Row('single_room_count', 'double_room_count',
                         'triple_room_count', css_class='flex flex-row gap-2'),

                     ),


            Fieldset(_('Persons'),
                     Row('adults', 'children',
                         'extra_seats', css_class='flex flex-row gap-2'),
                     Row('single_room_persons', 'double_room_persons',
                         'triple_room_persons', css_class='flex flex-row gap-2')
                     ),
        
            Fieldset(_('Personal Detail'),
                     'name',
                     'email',
                     Row('phone', 'phone2', css_class='flex flex-row gap-2 w-full')
                     ),
            'notes',
        )
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def get_initial(self):
        if self.kwargs.get('trip_id'):
            trip = get_object_or_404(Trip, id=self.kwargs.get('trip_id'))
            return {
                'trip': trip,
            }

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('trip_id'):
            context['trip'] = get_object_or_404(
                Trip, id=self.kwargs.get('trip_id'))
            return context
        return context


class trip_booking_detail(LoginRequiredMixin, DetailView):
    model = TripBooking
    template_name = 'reservation/booking/trip_booking_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        booking = self.get_object()
        context['payForm'] = PayTripBookingForm()
        return context