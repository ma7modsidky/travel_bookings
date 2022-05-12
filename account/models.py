from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.
USER_ROLES = (('gold', 'GOLD'), ('silver', 'SILVER'), ('bronze', 'BRONZE'))

class Organization(models.Model):
    name = models.CharField(max_length=25, db_index=True,
                            verbose_name=_('name'),)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    intro = models.TextField(null=True, blank=True)

    def __str__(self):
        return f'{self.name}'
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=20,
                            verbose_name=_('role'), choices=USER_ROLES)
    address = models.CharField(
        max_length=250, blank=True, verbose_name=_('address'),)
    phone_number = models.CharField(verbose_name=_('phone'), max_length=20,)
    phone_number_2 = models.CharField(
        blank=True, null=True, verbose_name=_('phone2'), max_length=20,)
    balance = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Balance'),
        default=0,
    )
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL , blank=True, null=True)
    total_bookings_done = models.PositiveBigIntegerField(
        verbose_name=_('Total bookings made by user'),
        blank=True, null=True,)
    percentage = models.FloatField(null=True,blank=True)    
    # will contain some info for users
    def __str__(self):
        return f'Profile for user {self.user.username}'


      