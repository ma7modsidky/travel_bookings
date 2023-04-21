
from audioop import reverse
from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from .models import Bus, BusBooking , Seat
from reservation.models import Destination, TripBooking , Booking
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Div, Field, HTML
from django.utils.translation import gettext_lazy as _
from actions.utils import create_action
# Create your views here.

class bus_list(ListView):
    model = Bus
    template_name = 'transport/bus/list.html'
    paginate_by = 10

    def get_queryset(self):
        t = self.kwargs.get('type')
        if t == 'going':
            if self.request.GET.get('date'):
                qs = Bus.objects.filter(date_1=self.request.GET.get('date'))
            else:    
                qs = Bus.objects.all().order_by('-date_1')
        elif t == 'return':
            if self.request.GET.get('date'):
                qs = Bus.objects.filter(date_2=self.request.GET.get('date'))
            else:    
                qs = Bus.objects.all().order_by('-date_2')
        else:
            qs = Bus.objects.all().order_by('-date_1')
        return qs

    def get_context_data(self, **kwargs):
        # Call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        # Add in a QuerySet of all the books
        if self.kwargs.get("type"):
            context['type'] = self.kwargs.get("type")
        else:
            context['type'] = 'going'
        if self.request.GET.get('date'):
            context['date'] = self.request.GET.get('date')
        return context

class bus_detail(DetailView):
    model = Bus
    template_name = 'transport/bus/detail.html'

class bus_create(CreateView):
    model = Bus
    fields = ['label', 'origin', 'destination',
              'date_1', 'date_2', 'start_location', 'start_time', 'description']
    template_name = 'transport/bus/create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            'label', 'origin', 'destination',
            HTML('<hr class="my-2">'),
            Field('date_1', ),
            Field('date_2', ),
            HTML('<hr class="my-2">'),
            'start_location', 'start_time', 'description',
        )
        form.helper.label_class = 'dark:text-gray-200'
        
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

def bus_select(request,booking_id, booking_type):
    if booking_type == 'trip':
        booking = TripBooking.objects.get(id=booking_id)
        buses = Bus.objects.filter(
            date_1=booking.trip.date_from, date_2=booking.trip.date_until, destination=booking.trip.destination)
        return render(request, 'transport/bus/bus_select.html', {'booking': booking, 'buses': buses
                                                                 })
    elif booking_type == 'individual':
        booking = Booking.objects.get(id=booking_id)
        buses = Bus.objects.filter(
            date_1=booking.date_from, date_2=booking.date_until, destination=booking.accommodation.destination)
        return render(request, 'transport/bus/bus_select_i.html', {'booking': booking, 'buses': buses
                                                                 })
    else:
        return render(request, 'transport/bus/bus_select.html', {
                                                                 })
    return render(request, 'transport/bus/bus_select.html', {'booking': booking, 'buses': buses
                                                                         })


def seats_select(request, booking_id, bus_id, booking_type):
    bus = Bus.objects.get(id=bus_id)
    if booking_type == 'trip':
        booking = TripBooking.objects.get(id=booking_id)
        url = 'transport/bus/seats_select.html'
        if booking.trip.date_from != bus.date_1 or booking.seats_booked:
            return redirect(booking)

    else :
        booking = Booking.objects.get(id=booking_id)
        url = 'transport/bus/seats_select_i.html'
        if booking.date_from != bus.date_1 or booking.seats_booked:
            return redirect(booking)
    if request.method == 'POST':
        if booking.get_total_seats  == len(request.POST.getlist('seat')):
            if booking_type == 'trip':
                for seat in request.POST.getlist('seat'):
                    Seat.objects.create(Bus=bus, booking=booking,
                                        number=seat, booking_type=booking_type, seat_type='going')
                    Seat.objects.create(Bus=bus, booking=booking,
                                        number=seat, booking_type=booking_type, seat_type='return')
            else:
                for seat in request.POST.getlist('seat'):
                    Seat.objects.create(Bus=bus, ibooking=booking,
                                        number=seat, booking_type=booking_type, seat_type='going')
                    Seat.objects.create(Bus=bus, ibooking=booking,
                                        number=seat, booking_type=booking_type, seat_type='return')
            booking.seats_booked = True
            booking.save()    
            return redirect(booking)
        else:
            msg = _('please select the right number of seats for this booking')
            return render(request, url, {'booking': booking, 'bus': bus, 'msg': msg,
                                                                    })
    else:
        return render(request, url, {'booking': booking, 'bus': bus
                                                             })

def bus_bookings(request,bus_id,seat_type):
    bus = Bus.objects.get(id=bus_id)
    seats = Seat.objects.filter(Bus=bus,seat_type=seat_type)
    
    bookings = TripBooking.objects.filter(
        bus_seats__in=seats, bus_seats__Bus=bus, bus_seats__seat_type=seat_type).distinct()
    ibookings = Booking.objects.filter(
        bus_seats__in=seats, bus_seats__Bus=bus, bus_seats__seat_type=seat_type).distinct()
    
    url = 'transport/seat/bus_bookings.html'
    return render(request, url, {'seats': seats, 'bus': bus, 'bookings': bookings, 'ibookings': ibookings, 'seat_type': seat_type
                                 })


def bus_booking_html(request, bus_id, seat_type):
    bus = Bus.objects.get(id=bus_id)
    seats = Seat.objects.filter(Bus=bus, seat_type=seat_type)

    bookings = TripBooking.objects.filter(
        bus_seats__in=seats, bus_seats__Bus=bus, bus_seats__seat_type=seat_type).distinct()
    ibookings = Booking.objects.filter(
        bus_seats__in=seats, bus_seats__Bus=bus, bus_seats__seat_type=seat_type).distinct()

    url = 'transport/rooming_list.html'
    return render(request, url, {'seats': seats, 'bus': bus, 'bookings': bookings, 'ibookings': ibookings, 'seat_type': seat_type
                                }) 

# Bus only booking
class bus_only_booking_create(CreateView):
    model = BusBooking
    fields = ['seats_count', 'name', 'phone', 'phone2',
              'notes']
    template_name = 'transport/bus_booking/create.html'

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            'seats_count', 'name', 'phone', 'phone2',
            HTML('<hr class="my-2">'),
            Field('notes', ),

        )
        form.helper.label_class = 'dark:text-gray-200'

        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form


    def form_valid(self, form):
        form.instance.Bus = Bus.objects.get(id=self.kwargs.get('bus_id'))
        booking = form.save(commit=True)
        verb = _('created bus only booking to bus')
        create_action(self.request.user,
                      f'{verb} {form.instance.Bus}', booking)
        return super().form_valid(form)

    def get_success_url(self):
        return reverse_lazy('transport:bus_detail', kwargs={'pk': self.kwargs.get('bus_id')})


class bus_only_booking_detail(DetailView):
    model = BusBooking
    template_name = 'transport/bus_booking/detail.html'

class bus_delete(DeleteView):
    model = Bus
    template_name = "reservation/confirm_delete.html"
    success_url = reverse_lazy('transport:bus_list')

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(bus_delete, self).get_object()
        verb = _('Deleted Bus')
        create_action(self.request.user, f'{verb} {obj}', obj)
        return obj


def seats_select_other(request, booking_id, bus_id):
    bus = Bus.objects.get(id=bus_id)
    booking = BusBooking.objects.get(id=booking_id)
    url = 'transport/bus/seats_select_o.html'
    if request.method == 'POST':
        if booking.seats_count == len(request.POST.getlist('seat')):
            for seat in request.POST.getlist('seat'):
                Seat.objects.create(Bus=bus, bus_only_booking=booking,
                                    number=seat, booking_type='other', seat_type='going')
                Seat.objects.create(Bus=bus, bus_only_booking=booking,
                                    number=seat, booking_type='other', seat_type='return')
                
            booking.seats_booked = True
            booking.save()
            return redirect(booking)
        else:
            msg = _('please select the right number of seats for this booking')
            return render(request, url, {'booking': booking, 'bus': bus, 'msg': msg,
                                         })
    else:
        return render(request, url, {'booking': booking, 'bus': bus
                                     })
