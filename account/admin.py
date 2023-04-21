from django.contrib import admin
from .models import Profile, Organization

# Register your models here.

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user',]

    class Meta:
       model = Profile


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', ]

    class Meta:
       model = Organization
