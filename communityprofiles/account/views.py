from django.contrib import messages
from django.contrib.auth import views as auth_views

from . import forms


DEFAULT_REDIRECT = "/"


def login(request):
    response =  auth_views.login(
        request,
        authentication_form=forms.AuthenticationForm,
        template_name="account/login.html")

    return response



def logout(request):
    response = auth_views.logout(request, next_page=DEFAULT_REDIRECT)

    if response.status_code == 302:
        messages.success(request, "You are signed out.")

    return response



def password_change(request):
    response =  auth_views.password_change(
        request,
        template_name="account/password_change_form.html",
        password_change_form=forms.PasswordChangeForm,
        post_change_redirect=DEFAULT_REDIRECT)

    if response.status_code == 302:
        messages.success(request, "Your password has been changed.")

    return response



def password_reset(request):
    response =  auth_views.password_reset(
        request,
        template_name="account/password_reset_form.html",
        email_template_name="account/password_reset_email.txt",
        password_reset_form=forms.PasswordResetForm,
        post_reset_redirect=DEFAULT_REDIRECT)

    if response.status_code == 302:
        messages.success(
            request,
            "Your password reset request has been received. "
            "Check your email for further instructions.")

    return response



def password_reset_confirm(request, uidb36, token):
    response = auth_views.password_reset_confirm(
        request, uidb36, token,
        template_name="account/password_reset_confirm.html",
        set_password_form=forms.SetPasswordForm,
        post_reset_redirect=DEFAULT_REDIRECT)

    if response.status_code == 302:
        messages.success(request, "Your password has been changed.")

    return response

