import base64
import hashlib

from django.contrib.auth import forms as auth_forms
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

import registration.forms as registration_forms
import floppyforms as forms

from communityprofiles.forms import FloppyWidgetsMixin, NonFieldErrorsMixin



class AuthenticationForm(FloppyWidgetsMixin,
                         NonFieldErrorsMixin,
                         auth_forms.AuthenticationForm):
    pass



class PasswordResetForm(FloppyWidgetsMixin,
                        NonFieldErrorsMixin,
                        auth_forms.PasswordResetForm):
    widget_classes = {"email": forms.EmailInput}



class SetPasswordForm(FloppyWidgetsMixin,
                      NonFieldErrorsMixin,
                      auth_forms.SetPasswordForm):
    pass



class PasswordChangeForm(FloppyWidgetsMixin,
                         NonFieldErrorsMixin,
                         auth_forms.PasswordChangeForm):
    pass


class RegistrationForm(FloppyWidgetsMixin,
                       NonFieldErrorsMixin,
                       registration_forms.RegistrationForm):
    username = forms.CharField(
        max_length=30,
        widget=forms.HiddenInput(),
        required=False,
        label=_("Username"),
        error_messages={
            'invalid': _("This value must contain only letters, numbers and underscores.")
        }
    )

    email = forms.EmailField(max_length=75,
                             label=_("Email address (this will be your username)"))
    first_name = forms.CharField(max_length=30)
    last_name = forms.CharField(max_length=30)
    tos = forms.BooleanField(widget=forms.CheckboxInput(),
                             label=_(u'I have read and agree to the Terms of Service'),
                             error_messages={'required': _("You must agree to the terms to register")})

    is_general_public = forms.BooleanField(required=False, label=_(u'General Public'))
    is_community_advocate = forms.BooleanField(required=False, label=_(u'Community Advocate'))
    is_journalist = forms.BooleanField(required=False, label=_(u'Journalist'))
    is_researcher = forms.BooleanField(required=False, label=_(u'Researcher'))
    is_grant_writer = forms.BooleanField(required=False, label=_(u'Grant Writer'))
    is_city_state_agency_staff = forms.BooleanField(required=False, label=_(u'City / State Agency Staff'))
    is_consultant = forms.BooleanField(required=False, label=_(u'Consultant'))
    is_legislator = forms.BooleanField(required=False, label=_(u'Legislator'))
    is_policy_analyst = forms.BooleanField(required=False, label=_(u'Policy Analyst'))
    is_other = forms.BooleanField(required=False, label=_(u'Other'))
    organization = forms.CharField(max_length=300,required=False)
    org_is_non_profit = forms.BooleanField(required=False, label=_(u'Non-Profit'))
    org_is_state_city_agency = forms.BooleanField(required=False, label=_(u'City / State Agency'))
    org_is_university = forms.BooleanField(required=False, label=_(u'University'))
    org_is_other = forms.BooleanField(required=False, label=_(u'Other'))
    wants_notifications = forms.BooleanField(required=False, label=_(u"I'd like to receive notifications about trainings, new datasets, and general Profiles news"))

    def clean_email(self):
        """
        Validate that the supplied email address is unique for the
        site.
        
        """
        if User.objects.filter(email__iexact=self.cleaned_data['email']):
            raise forms.ValidationError(_("This email address is already in use. Please supply a different email address."))
        return self.cleaned_data['email']

    def clean(self):
        """
        Verifiy that the values entered into the two password fields
        match. Note that an error here will end up in
        ``non_field_errors()`` because it doesn't apply to a single
        field.
         
        """
        if 'password1' in self.cleaned_data and 'password2' in self.cleaned_data:
            if self.cleaned_data['password1'] != self.cleaned_data['password2']:
                raise forms.ValidationError(_("The two password fields didn't match."))
  
        # hash the user's email address to use as a username
        m = hashlib.md5()
        m.update(self.cleaned_data['email'])
        self.cleaned_data['username'] = base64.b64encode(m.digest())
        return self.cleaned_data

