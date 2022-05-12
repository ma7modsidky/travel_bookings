from random import choices
from django import forms
from django.contrib.auth.models import User
from .models import Organization, Profile
from django.utils.translation import gettext_lazy as _
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Fieldset, Row, Div, Field
USER_ROLES = (('gold', 'GOLD'), ('silver', 'SILVER'), ('bronze', 'BRONZE'))



class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)

class UserRegistrationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.add_input(
            Submit('submit', _('Create'), css_class='focus:outline-none text-white bg-red-700 hover:bg-red-800 focus:ring-4 focus:ring-red-300 font-medium rounded-lg text-sm px-5 py-2.5 mr-2 mb-2 dark:bg-red-600 dark:hover:bg-red-700 dark:focus:ring-red-900 cursor-pointer my-4'))
        self.label_class = 'dark:text-white bg-red-500'
        self.fields['role'].widget.attrs.update({'class': 'px-10'})
        

    password = forms.CharField(label=_('Password'), widget=forms.PasswordInput)
    password2 = forms.CharField(label=_('Repeat password'), widget=forms.PasswordInput)
    role = forms.ChoiceField(label=_('Role'), choices=USER_ROLES,
                           )
    address = forms.CharField(label=_('address'), required=False
                              )
    phone_number = forms.CharField(label=_('phone'),
                                   )
    phone_number_2 = forms.CharField(label=_('phone'),
                                     required=False
                                     )
    org = forms.ModelChoiceField(queryset=Organization.objects.all(),
                                 to_field_name='name',
                                 empty_label="Select Organization",
                                 )
    percentage = forms.FloatField()

    
    class Meta:
        model = User
        fields = ('username', 'first_name','last_name' ,'email')
    def clean_password2(self):
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Passwords don\'t match.')
        return cd['password2']
    
    
class UserEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email')
        
class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ('role', 'address', 'phone_number',
                  'phone_number_2', 'org', 'percentage')
