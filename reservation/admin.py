from django.contrib import admin
from .models import Destination, Hotel, Booking, AccommodationType, HotelPackage, Trip, TripBooking, TripProgram, TripBookingProgram
# Register your models here.


@admin.register(Destination)
class DestinationAdmin(admin.ModelAdmin):
    list_display = ('name',)
    prepopulated_fields = {'slug': ('name',)}
    class Meta:
        model = Destination


class HotelPackageStackAdmin(admin.StackedInline):
    model = HotelPackage

@admin.register(Hotel)
class HotelAdmin(admin.ModelAdmin):
    list_display = ('name', 'destination')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [HotelPackageStackAdmin]
    readonly_fields = ('get_packages',)
    class Meta:
        model = Hotel


@admin.register(AccommodationType)
class AccommodationTypeAdmin(admin.ModelAdmin):
    class Meta:
        model = AccommodationType


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('pk', 'name','accommodation','adults',
                    'date_from', 'time_period', 'transport')
    list_filter = ('date_from', 'accommodation', 'transport')
    extra_fields = ['get_packages']
    readonly_fields = ('calculate_remaining_amount',)
    search_fields = ['phone']
    class Meta:
        model = Booking
        

@admin.register(TripBooking)
class TripBookingAdmin(admin.ModelAdmin):
    list_display = ('id','__str__')
    # list_filter = ('date_from', 'accommodation', 'transport')
    extra_fields = ['']
    readonly_fields = ('get_total_seats', 'get_person_count',
                       'get_primary_price', 'get_primary_price_after_discount', 'get_extra_seats_price', 'get_total_price', 'get_remained_price', 'get_programs_price')
    # search_fields = ['phone']

    class Meta:
        model = TripBooking


@admin.register(HotelPackage)
class HotelPackageAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'accommodation_type',
                    'label', 'date_from', 'date_to')
    class Meta:
        model = HotelPackage


@admin.register(Trip)
class TripAdmin(admin.ModelAdmin):
    list_display = ('id','destination', 'accommodation', 'date_from', 'date_until',
                    'bus_total',)
    list_filter = ('date_from', 'accommodation')
    readonly_fields = ('get_price_per_person',)
    search_fields = ['accommodation__name']

    class Meta:
        model = Booking


@admin.register(TripProgram)
class TripProgramAdmin(admin.ModelAdmin):
    class Meta :
        model = TripProgram


@admin.register(TripBookingProgram)
class TripProgramAdmin(admin.ModelAdmin):
    class Meta:
        model = TripBookingProgram

