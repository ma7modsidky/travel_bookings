from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm
from django.contrib.auth.decorators import login_required
from .models import Profile
from django.contrib import messages

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User

#ajax views follow/unfollow
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.utils.translation import gettext_lazy as _
import json


# Create your views here.

def user_login(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request,username=cd['username'],
                                        password=cd['password'])
            if user is not None:
                if user.is_active:
                    login(request, user)
                    return HttpResponse('Authenticated '\
                    'successfully')
                else:
                    return HttpResponse('Disabled account')
            else:
                return HttpResponse('Invalid login')
    else:
        form = LoginForm()
    return render(request, 'account/login.html', {'form': form})

@login_required
def dashboard(request):
    # Display all actions by default
    return render(request,
                  'account/dashboard.html',
                  {})

def register(request):
    if request.method == 'POST':
        user_form = UserRegistrationForm(request.POST)
        if user_form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = user_form.save(commit=False)
            # Set the chosen password
            new_user.set_password(user_form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            # Create the User profile
            Profile.objects.create(
                user=new_user, role=user_form.cleaned_data['role'], address=user_form.cleaned_data['role'], phone_number=user_form.cleaned_data['phone_number'], phone_number_2=user_form.cleaned_data['phone_number_2'], org=user_form.cleaned_data['org'], percentage=user_form.cleaned_data['percentage'],)
            return redirect('/account/users/')
    else :
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})
            
@login_required
def edit(request):
    if request.method == 'POST':
        user_form = UserEditForm(instance=request.user, 
                                 data=request.POST)
        profile_form = ProfileEditForm(instance=request.user.profile,
                                        data=request.POST,
                                        files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated \'successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        user_form = UserEditForm(instance=request.user)
        profile_form = ProfileEditForm(instance=request.user.profile) 
    return render(request,'account/edit.html', {'user_form': user_form,
                                                'profile_form': profile_form})

@login_required
def user_list(request):
    if request.GET.get('type') == 'active':
        users = User.objects.filter(is_active=True)
    elif request.GET.get('type') == 'inactive':
        users = User.objects.filter(is_active=False)
    else:
        users = User.objects.all()
        return render(request, 'account/user/list.html', {'section': 'people',
                                                      'users': users})
    
@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html', {'section': 'people', 
                                                        'user': user})



    