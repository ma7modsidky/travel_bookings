from django.db import models
from reservation.models import Destination , Trip ,TripBooking
from django.core.validators import MinValueValidator, MaxValueValidator
from datetime import  date
from django.utils.translation import gettext_lazy as _
# Create your models here.
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

class Seat(models.Model):
    Bus = models.ForeignKey(
        Bus, related_name='seats', on_delete=models.CASCADE)
    number = models.PositiveBigIntegerField(validators=[
        MinValueValidator(1),
        MaxValueValidator(49)])
    booking = models.ForeignKey(
        TripBooking, related_name='bus_seats', on_delete=models.CASCADE)

    class Meta:
        constraints = [
            models.UniqueConstraint(
                fields=['Bus', 'number'],
                name='unique seat'
            )
        ]

    def __str__(self) -> str:
        return f'Seat[{self.number}] in Bus[{self.Bus.id}] -- Booking[{self.booking.id}]'
