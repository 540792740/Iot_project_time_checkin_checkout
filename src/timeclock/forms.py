from datetime import timedelta
from django.conf import settings
from django import forms
from django.contrib.auth import get_user_model
from django.utils import timezone
from.models import UserActivity

ACTIVITY_TIME_DETLA = getattr(settings, "ACTIVITY_TIME_DETLA", timedelta(minutes=1)) 

User = get_user_model()

class UserActivityForm(forms.Form):
    username = forms.CharField(widget=forms.HiddenInput)
    password = forms.CharField(label='Verify Password', widget=forms.PasswordInput)
    def clean(self, *args, **kwargs):
        cleaned_data = super(UserActivityForm, self).clean(*args, **kwargs)
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        qs = User.objects.filter(username__iexact=username)
        if not qs.exists() or qs.count() != 1:
            raise forms.ValidationError("This password is incorrect")
        else:
            user_obj = qs.first()
            current = UserActivity.objects.current(user_obj)
            if current:
                actual_obj_time = current.timestamp
                the_delta = ACTIVITY_TIME_DETLA
                diff = the_delta + actual_obj_time
                now = timezone.now()
                if diff > now:
                    raise forms.ValidationError("You must wait {time} before this action".format(time=the_delta))
 
            if not user_obj.check_password(password):
                raise forms.ValidationError("This password is incorrect")
        return cleaned_data


#init a login form
class LoginForm(forms.Form):
    username = forms.CharField()
    password = forms.CharField(widget=forms.PasswordInput)
    
    def clean(self, *args, **kwargs):
        cleaned_data = super(LoginForm, self).clean(*args, **kwargs)
        username = cleaned_data.get('username')
        password = cleaned_data.get('password')
        qs = User.objects.filter(username__iexact=username)
        if not qs.exists() or qs.count() != 1:
            raise forms.ValidationError("This username/password is incorrect")
        else:
            user_obj = qs.first()
            if not user_obj.check_password(password):
                raise forms.ValidationError("This username/password is incorrect")
        return cleaned_data
