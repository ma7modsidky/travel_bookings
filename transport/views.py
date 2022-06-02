from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.shortcuts import get_object_or_404, redirect
from .models import Bus , Seat
from reservation.models import Destination, TripBooking
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Div, Field, HTML
from django.utils.translation import gettext_lazy as _
# Create your views here.

class bus_list(ListView):
    model = Bus
    template_name = 'transport/bus/list.html'
    paginate_by = 10

    def get_queryset(self):
        t = self.kwargs.get('type')
        if t == 'going':
            qs = Bus.objects.all().order_by('-date_1')
        elif t == 'return':
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

def bus_select(request,booking_id):
    booking = TripBooking.objects.get(id=booking_id)
    # buses = Bus.objects.all()
    buses = Bus.objects.filter(
        date_1=booking.trip.date_from, date_2=booking.trip.date_until, destination=booking.trip.destination)
    return render(request, 'transport/bus/bus_select.html', {'booking': booking, 'buses': buses
                                                                         })

def seats_select(request,booking_id,bus_id):
    booking = TripBooking.objects.get(id=booking_id)
    bus = Bus.objects.get(id=bus_id)
    if booking.trip.date_from != bus.date_1 or booking.seats_booked:
        return redirect(booking)
    if request.method == 'POST':
        if booking.get_total_seats  == len(request.POST.getlist('seat')):
            for seat in request.POST.getlist('seat'):
                Seat.objects.create(Bus=bus, booking=booking, number=seat)
            booking.seats_booked = True
            booking.save()    
            return redirect(booking)
        else:
            msg = 'please select the right number of seats for this booking'
            print('numbre false')
            print(request.POST.getlist('seat'))
            return render(request, 'transport/bus/seats_select.html', {'booking': booking, 'bus': bus, 'msg':msg,
                                                                    })
    else:
        return render(request, 'transport/bus/seats_select.html', {'booking': booking, 'bus': bus
                                                             })
