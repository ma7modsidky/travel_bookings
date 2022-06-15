from django.db import models
from reservation.models import Destination , Trip ,TripBooking , Booking
from django.core.validators import MinValueValidator, MaxValueValidator
from django.core.exceptions import ValidationError
from datetime import  date
from django.utils.translation import gettext_lazy as _
# Create your models here.
BOOKING_TYPE = (('trip', 'TRIP'), ('individual', 'INDIVIDUAL'),('other','OTHER'))
SEAT_TYPE = (('going','GOING'),('return','RETURN'),('both','BOTH'))
class Bus(models.Model):
    label = models.CharField(max_length=100)
    date_1 = models.DateField()
    date_2 = models.DateField()
    start_location = models.CharField(max_length=100)
    start_time = models.CharField(max_length=100)
    destination = models.ForeignKey(Destination, related_name='buses_to' , on_delete=models.CASCADE)
    origin = models.ForeignKey(
        Destination, related_name='buses_from', on_delete=models.CASCADE)
    description = models.TextField(null=True,blank=True)

    class Meta:
        ordering = ['-date_1']

    def __str__(self) -> str:
        return f'[{self.id}]{self.label} ({self.date_1}) >> ({self.date_2})'
    def get_going_state(self):
        if self.date_1 > date.today():
            return 'upcoming'
        if self.date_1 == date.today():
            return 'ongoing'   
        else:
            return 'previous'

    def get_return_state(self):
        if self.date_2 > date.today():
            return 'upcoming'
        if self.date_2 == date.today():
            return 'ongoing'
        else:
            return 'previous'


class BusBooking(models.Model):
    Bus = models.ForeignKey(
        Bus, related_name='bus_only_bookings', on_delete=models.RESTRICT, null=True)
    name = models.CharField(verbose_name=_('Name'),
                            max_length=50,
                            )
    phone = models.CharField(
        verbose_name=_('Phone number'),
        max_length=256,
    )
    phone2 = models.CharField(
        verbose_name=_('Additional Phone number'),
        max_length=256,
        blank=True,
    )
    notes = models.TextField(
        max_length=1024,
        verbose_name=_('Notes'),
        blank=True,
    )
    seats_count = models.PositiveIntegerField()
    seats_booked = models.BooleanField(default=False)

    def __str__(self) -> str:
        return f'{self.seats_count} seats at Bus[{self.Bus.id}] ({self.Bus.date_1})'
class Seat(models.Model):
    Bus = models.ForeignKey(
        Bus, related_name='seats', on_delete=models.CASCADE)
    number = models.PositiveBigIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(49)])
    booking_type = models.CharField(max_length=15, choices=BOOKING_TYPE)
    seat_type = models.CharField(max_length=15, choices=SEAT_TYPE)
    booking = models.ForeignKey(
        TripBooking, related_name='bus_seats', on_delete=models.CASCADE, null=True, blank=True)
    ibooking = models.ForeignKey(
        Booking, related_name='bus_seats', on_delete=models.CASCADE, null=True, blank=True)
    bus_only_booking = models.ForeignKey(
        BusBooking, related_name='bus_seats', on_delete=models.CASCADE, null=True, blank=True)
    def clean(self):
        if self.booking and self.ibooking :
            raise ValidationError(
                _('cannot have two bookings in the same seat'))
    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['Bus', 'number', 'seat_type'],
                name='unique seat'
            )
        ]

    # def __str__(self) -> str:
    #     return f'Seat[{self.number}] in Bus[{self.Bus.id}] -- Booking[{self.booking.id}]'


