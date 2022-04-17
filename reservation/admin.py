from django.contrib import admin
from .models import Destination,Hotel, Booking, AccommodationType, HotelPackage
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
        




@admin.register(HotelPackage)
class HotelPackageAdmin(admin.ModelAdmin):
    list_display = ('hotel', 'accommodation_type',
                    'label', 'date_from', 'date_to')
    class Meta:
        model = HotelPackage

