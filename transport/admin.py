from django.contrib import admin
from .models import Bus, Seat , BusBooking
# Register your models here.


@admin.register(Bus)
class BusAdmin(admin.ModelAdmin):

    class Meta:
        model = Bus


@admin.register(Seat)
class BusAdmin(admin.ModelAdmin):

    class Meta:
        model = Seat


@admin.register(BusBooking)
class BusBookingAdmin(admin.ModelAdmin):

    class Meta:
        model = BusBooking
