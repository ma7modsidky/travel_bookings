from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from requests import request
from .forms import LoginForm, UserRegistrationForm, UserEditForm, ProfileEditForm , OrgForm
from django.contrib.auth.decorators import login_required , permission_required
from .models import Organization, Profile
from django.contrib import messages

from django.shortcuts import get_object_or_404
from django.contrib.auth.models import User, Group

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


@login_required
@permission_required({("auth.add_user"), ("account.add_profile")}
    )
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
            # add user to group
            g = Group.objects.get(name=user_form.cleaned_data['role'])
            g.user_set.add(new_user)
            # Create the User profile
            Profile.objects.create(
                user=new_user, role=user_form.cleaned_data['role'], address=user_form.cleaned_data['role'], phone_number=user_form.cleaned_data['phone_number'], phone_number_2=user_form.cleaned_data['phone_number_2'], org=user_form.cleaned_data['org'], percentage=user_form.cleaned_data['percentage'],)
            return redirect('/account/users/')
    else :
        user_form = UserRegistrationForm()
    return render(request, 'account/register.html', {'user_form': user_form})


@login_required
@permission_required({("auth.add_user"), ("account.add_profile")}
 )
def edit(request, user_id=None):
    if request.method == 'POST':
        # another user
        if user_id:
            user = User.objects.get(id=user_id)
            role = user.profile.role
            user_form = UserEditForm(instance=user,
                                     data=request.POST)
            profile_form = ProfileEditForm(instance=user.profile,
                                           data=request.POST,
                                           files=request.FILES)
        # our own user    
        else:
            user = request.user
            role = user.profile.role
            user_form = UserEditForm(instance=request.user, 
                                    data=request.POST)
            profile_form = ProfileEditForm(instance=request.user.profile,
                                            data=request.POST,
                                            files=request.FILES)
        if user_form.is_valid() and profile_form.is_valid():
            print(role)
            print(profile_form.cleaned_data['role'])
            if role != profile_form.cleaned_data['role']:
                print('role changed')
                old_group = Group.objects.get(name=role)
                new_group = Group.objects.get(
                    name=profile_form.cleaned_data['role'])
                old_group.user_set.remove(user)
                new_group.user_set.add(user)
            else:
                print('role didnt change')
            user_form.save()
            profile_form.save()
            messages.success(request, 'Profile updated \'successfully')
        else:
            messages.error(request, 'Error updating your profile')
    else:
        if user_id:
            user = User.objects.get(id=user_id)
            user_form = UserEditForm(instance=user,
                                     )
            profile_form = ProfileEditForm(instance=user.profile,
                                           )
        else:
            user = request.user
            user_form = UserEditForm(instance=request.user)
            profile_form = ProfileEditForm(instance=request.user.profile) 
    return render(request,'account/edit.html', {'user_form': user_form,
                                                'profile_form': profile_form,
                                                'u':user})


@permission_required({("auth.add_user"), ("account.add_profile")}
                     )
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
def org_list(request):
    orgs = Organization.all()
    return render(request, 'account/orgs/list.html', {
        'orgs': orgs})

@login_required
def org_detail(request,pk):
    org = Organization.objects.get(id=pk)
    return render(request, 'account/orgs/detail.html', {
        'org': org})

def org_create(request):
    if request.method == 'POST':
        org = OrgForm(request.POST)
        if org.is_valid():
            org.save(commit=True)
            return redirect('/account/orgs/')
    else:    
        org = OrgForm()
    return render(request, 'account/orgs/create.html', {'org': org})
    
@permission_required({("auth.add_user"), ("account.add_profile")}
                     )
@login_required
def user_detail(request, username):
    user = get_object_or_404(User, username=username, is_active=True)
    return render(request, 'account/user/detail.html', {
                                                        'user': user})

@login_required
def profile(request):
    user = get_object_or_404(User, id=request.user.id)
    return render(request, 'account/user/profile.html', {'section': 'people', 
                                                        'user': user})



    