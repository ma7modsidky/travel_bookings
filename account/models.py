from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

# Create your models here.

class Organization(models.Model):
    name = models.CharField(max_length=25, db_index=True)
    slug = models.SlugField(max_length=250, unique=True, db_index=True)
    intro = models.TextField(null=True, blank=True)
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    role = models.CharField(max_length=250, blank=True)
    address = models.CharField(max_length=250, blank=True)
    phone_number = PhoneNumberField()
    phone_number_2 = PhoneNumberField(blank=True,null=True)
    balance = models.DecimalField(
        max_digits=36,
        decimal_places=0,
        verbose_name=_('Balance'),
        blank=True, null=True,
    )
    org = models.ForeignKey(Organization, on_delete=models.SET_NULL , blank=True, null=True)
    # will contain some info for users
    def __str__(self):
        return f'Profile for user {self.user.username}'


      