from django.db import models
from django.conf import settings
from django.contrib.auth import get_user_model

# Create your models here.
class Profile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    # will contain some info for users
    def __str__(self):
        return f'Profile for user {self.user.username}'


      