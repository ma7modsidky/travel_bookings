
from gc import disable
from urllib import response
from django.http import JsonResponse
from pyexpat import model
from django.shortcuts import get_object_or_404, redirect
from django.shortcuts import render
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, DeleteView, UpdateView
from django.urls import reverse_lazy
from django.views.generic.edit import DeleteView
from django.conf import settings
from django import http
from .models import Destination, Hotel, HotelPackage, Trip, TripBooking, TripBookingProgram , Booking
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils import timezone
from datetime import datetime, timedelta, date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Div, Field
from crispy_tailwind import layout
from .forms import PayTripBookingForm
from django.utils.translation import gettext_lazy as _
from actions.utils import create_action
from account.models import Profile
from django.template.loader import render_to_string
import weasyprint
from django.http import HttpResponse
from django.contrib.auth.mixins import PermissionRequiredMixin
# Create your views here.


def home(request):
    return render(request, 'reservation/home.html', {})

def reservations_page(request):
    return render(request, 'reservation/misc/reservations_page.html', {})

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

class trip_create(LoginRequiredMixin, CreateView):
    model = Trip
    fields = ['destination', 'accommodation', 'date_from',
              'date_until', 'rooms_total', 'bus_total', 'meeting_location', 'transport_price_person', 'single_room_price', 'double_room_price', 'triple_room_price', 'single_room_cost', 'double_room_cost', 'triple_room_cost']
    template_name = 'reservation/trip/trip_create.html'
    exclude = ['creation_user']

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            Field('destination',
                  css_class='text-center destination'), 'accommodation',
            Field('date_from', datepicker=True, readonly='readonly', id="date_start",
                  template='reservation/datepicker.html', ),
            Field('date_until', datepicker=True, datepicker_format='mm/dd/yyyy', readonly='readonly', id="date_until",
                  template='reservation/datepicker.html', ),
            Fieldset(_('Trip Information'),
                     Row('rooms_total', 'bus_total',
                         css_class='flex flex-row gap-2'),
                     'meeting_location',
                     ),
            Fieldset(_('Cost'),
                     Row('single_room_cost', 'double_room_cost',
                         'triple_room_cost', css_class='flex flex-row gap-2')
                     ),
            Fieldset(_('Price'),
                     Row('transport_price_person'),
                     Row('single_room_price', 'double_room_price',
                         'triple_room_price', css_class='flex flex-row gap-2')
                     ),
        )
        # form.helper.Field('date_from',readonly='readonly', id="date_start", template='reservation/datepicker.html')
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        return super().form_valid(form)
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
        create_action(self.request.user, 'deleted', obj)
        return obj


class trip_booking_create(LoginRequiredMixin, PermissionRequiredMixin, CreateView):
    model = TripBooking
    fields = ['trip', 'single_room_count', 'double_room_count', 'triple_room_count', 'adults', 'children',
              'extra_seats', 'single_room_persons', 'double_room_persons', 'triple_room_persons', 'seats', 'name', 'email', 'phone', 'phone2', 'notes', 'discount_percentage', 'discount_amount', 'paid_amount']
    template_name = 'reservation/booking/trip_booking_create.html'
    exclude = ['creation_user']
    permission_required = ('reservation.add_tripbookings')

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
                                             Row('phone', 'phone2',
                                                 css_class='flex flex-row gap-2 w-full')
                                             ),
                                    'notes',
                                    'seats',
                                    'discount_percentage', 'discount_amount',
                                    'paid_amount',
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
        create_action(self.request.user,
                      f'made trip booking {form.instance.trip}', self.object)
        profile = Profile.objects.get(user=self.request.user)
        profile.balance += form.instance.paid_amount
        profile.save()
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
class trip_booking_delete(DeleteView):
    model = TripBooking
    template_name = "reservation/confirm_delete.html"
    success_url = reverse_lazy('reservation:trip_list', kwargs={'time': 'all'})

    def get_object(self, queryset=None):
        """ Hook to ensure object is owned by request.user. """
        obj = super(trip_booking_delete, self).get_object()
        if not obj.creation_user == self.request.user:
            return http.HttpResponseForbidden("Cannot delete other's trips")
        create_action(self.request.user, f'deleted trip booking {obj}', obj)
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
    
class trip_booking_update(LoginRequiredMixin, UpdateView):
    model = TripBooking
    fields = ['trip', 'single_room_count', 'double_room_count', 'triple_room_count', 'adults', 'children',
              'extra_seats', 'single_room_persons', 'double_room_persons', 'triple_room_persons', 'seats', 'name', 'email', 'phone', 'phone2', 'notes', 'paid_amount']
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
                                             Row('phone', 'phone2',
                                                 css_class='flex flex-row gap-2 w-full')
                                             ),
                                    'notes',
                                    'seats',
                                    'paid_amount',
                                    )
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    

    def form_valid(self, form):
        create_action(self.request.user,
                      f'updated trip booking {form.instance.trip}', self.object)
        return super().form_valid(form)

def trip_booking_pay(request , pk):
    booking = get_object_or_404(TripBooking, id=pk)
    if request.method == 'POST':
        form = PayTripBookingForm(data=request.POST)
        if form.is_valid():
            amount = form.cleaned_data['amount']
            booking.paid_amount += form.cleaned_data['amount']
            booking.save()
            create_action(request.user,
                          f'recieved amount {amount}', booking)
            profile = Profile.objects.get(user = request.user)
            profile.balance += form.cleaned_data['amount']
            profile.save()
            return redirect(booking)
    else:
        # build form with data provided by the bookmarklet via GET
        form = PayTripBookingForm(data=request.GET)
    return render(request, 'reservation/booking/trip_booking_pay.html', {'object':booking,
                                                        'form': form})


class trip_booking_program_add(LoginRequiredMixin, CreateView):
    model = TripBookingProgram 
    fields = ['booking', 'program', 'quantity']
    template_name = 'reservation/booking/trip_booking_program_add.html'
    # success_url = reverse_lazy('reservation:trip_booking_detail', args=[1])
    def get_context_data(self, **kwargs):
        context= super().get_context_data(**kwargs)
        context['object'] = get_object_or_404(
            TripBooking, id=self.kwargs.get('pk'))
        return context

    def get_initial(self):
        booking = get_object_or_404(TripBooking, id=self.kwargs.get('pk'))
        return {
            'booking': booking,
        }

def invoice_pdf(request,pk):
    booking = get_object_or_404(TripBooking, id=pk)
    html = render_to_string('reservation/pdf/invoice.html',
                            {'object': booking})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=booking_{booking.id}.pdf'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
                                           )
    return response


def trip_bookings_list_pdf(request, pk):
    trip = get_object_or_404(Trip, id=pk)
    html = render_to_string('reservation/pdf/booking_list.html',
                            {'object': trip})
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'filename=trip_booking_list_{trip.id}.pdf'
    weasyprint.HTML(string=html, base_url=request.build_absolute_uri()).write_pdf(response,
                                                                                  )
    return response


#AJAX
def load_hotels(request): 
    destination = Destination.objects.get(id=request.GET.get(
        'destination_id'))
    hotels = Hotel.objects.filter(
        destination=destination)
    print(list(hotels.values('id', 'name')))
    # return render(request, 'persons/city_dropdown_list_options.html', {'cities': cities})
    return JsonResponse(list(hotels.values('id', 'name')), safe=False)


# Individual Booking
class booking_create(LoginRequiredMixin, CreateView):
    model = Booking
    fields = ['accommodation', 'package', 'accommodation_type','transport' ,'single_room_count','date_from','date_until' ,'double_room_count',  'triple_room_count', 'adults', 'children',
              'extra_seats', 'name', 'email', 'phone', 'notes', 'discount_percentage', 'discount_amount', 'paid_amount']
    template_name = 'reservation/booking/trip_booking_create.html'
    exclude = ['creation_user']
    # permission_required = ('')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            Row(Field('accommodation', readonly='readonly',css_class='min-w-[8rem]'), Field('package', readonly='readonly',css_class='min-w-[8rem]'),
                css_class='flex flex-row gap-2',),
            Row('accommodation_type', 'transport',
                css_class='flex flex-row gap-2'),
            Field('date_from', datepicker=True, readonly='readonly', id="date_start",
                  template='reservation/datepicker.html', ),
            Field('date_until', datepicker=True, datepicker_format='mm/dd/yyyy', readonly='readonly', id="date_until",
                  template='reservation/datepicker.html', ),
            Fieldset(_('Numbre of Rooms'),
                     Row('single_room_count', 'double_room_count',
                         'triple_room_count', css_class='flex flex-row gap-2'),
                     ),

            Fieldset(_('Persons'),
                     Row('adults', 'children',
                         'extra_seats', css_class='flex flex-row gap-2'),
                     ),

            Fieldset(_('Personal Detail'),
                     'name',
                     'email',
                     Row('phone',
                         css_class='flex flex-row gap-2 w-full')
                     ),
            'notes',
            'discount_percentage', 'discount_amount',
            'paid_amount',
        )
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def get_initial(self):
        if self.kwargs.get('hotel_id'):
            accommodation = get_object_or_404(
                Hotel, id=self.kwargs.get('hotel_id'))
        if self.kwargs.get('package_id'):
            package = get_object_or_404(
                HotelPackage, id=self.kwargs.get('package_id'))
        return {
            'accommodation': accommodation,
            'package': package,
        }

    def form_valid(self, form):
        form.instance.creation_user = self.request.user
        create_action(self.request.user,
                      f'made booking {form.instance}', self.object)
        profile = Profile.objects.get(user=self.request.user)
        profile.balance += form.instance.paid_amount
        profile.save()
        return super().form_valid(form)

class package_create(LoginRequiredMixin, CreateView):
    model = HotelPackage
    fields = ['hotel', 'label', 'date_from', 'date_until',
              'single_room_half', 'single_room_half_cost', 'single_room_full', 'single_room_full_cost', 'double_room_half', 'double_room_half_cost', 'double_room_full', 'double_room_full_cost', 'triple_room_half', 'triple_room_half_cost', 'triple_room_full', 'triple_room_full_cost']
    template_name = 'reservation/package/create.html'
    exclude = ['creation_user']
    # permission_required = ('')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)
        form.helper = FormHelper()
        form.helper.layout = Layout(
            Field('hotel',
                   ),
            'label',
            Field('date_from', datepicker=True, readonly='readonly', id="date_start",
                  template='reservation/datepicker.html', ),
            Field('date_until', datepicker=True, datepicker_format='mm/dd/yyyy', readonly='readonly',   id="date_until",
                  template='reservation/datepicker.html',),
            Fieldset(_('Prices per night'),
                     Row('single_room_half_cost', 'single_room_full_cost',
                         css_class='flex flex-row gap-3'),
                     Row('single_room_half', 'single_room_full',
                        css_class='flex flex-row gap-3'),
                     Row('double_room_half_cost', 'double_room_full_cost',
                         css_class='flex flex-row gap-3'),
                     Row('double_room_half', 'double_room_full',
                        css_class='flex flex-row gap-3'),
                     Row('triple_room_half_cost', 'triple_room_full_cost',
                         css_class='flex flex-row gap-3'),
                     Row('triple_room_half', 'triple_room_full',
                         css_class='flex flex-row gap-3'),
                     ),
        )
        form.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        return form

    def get_initial(self):
        hotel = get_object_or_404(
            Hotel, id=self.kwargs.get('hotel_id'))
        creation_user = self.request.user
        return {
            'hotel': hotel.id,
            'creation_user': creation_user,
        }

    def form_valid(self, form):
        print('valid')
        form.instance.creation_user = self.request.user
        form.save()
        create_action(self.request.user,
                      f'created package {form.instance}', self.object)
        return super().form_valid(form)

    def form_invalid(self, form):
        print(form.errors)
        return super().form_invalid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.kwargs.get('hotel_id'):
            context['hotel'] = get_object_or_404(
                Hotel, id=self.kwargs.get('hotel_id'))
            return context
        return context
class package_detail(LoginRequiredMixin, DetailView):
    model = HotelPackage
    template_name = 'reservation/package/detail.html'
class booking_detail(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'reservation/ibooking/detail.html'

class booking_list_package(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'reservation/ibooking/list.html'

    def get_queryset(self):
        qs = Booking.objects.filter(package=self.kwargs.get('package_id'))
        return qs

    def get_context_data(self, **kwargs) :
        context = super().get_context_data(**kwargs)
        package = HotelPackage.objects.get(id=self.kwargs.get('package_id'))
        context['package'] = package
        return context


def search_booking(request):
    if TripBooking.objects.filter(id=request.GET.get('trip_booking_id')).exists():
        return redirect(TripBooking.objects.get(id=request.GET.get('trip_booking_id')))
    else:
        return render(request, 'reservation/misc/reservations_page.html', {'no_result': True, 'q': request.GET.get('trip_booking_id')})
    
def search_ibooking(request):
    if Booking.objects.filter(id=request.GET.get('booking_id')).exists():
        return redirect(Booking.objects.get(id=request.GET.get('booking_id')))
    else:
        return render(request, 'reservation/misc/reservations_page.html', {'no_result_i': True, 'q': request.GET.get('booking_id')})


class trip_booking_list_all(LoginRequiredMixin, ListView):
    model = TripBooking
    template_name = 'reservation/misc/trip_booking_list_all.html'


class booking_list_all(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'reservation/misc/booking_list_all.html'
