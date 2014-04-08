from django.conf.urls.defaults import patterns, url
from django.views.generic.simple import direct_to_template

from registration.views import activate
from registration.views import register


urlpatterns = patterns(
    "communityprofiles.account.views",

    url(r"^login/$", "login", name="auth_login"),
    url(r"^logout/$", "logout", name="auth_logout"),

    url(r"^password_change/$",
        "password_change",
        name="auth_password_change"),

    url(r"^password_reset/$",
        "password_reset",
        name="auth_password_reset"),

    url(r"^reset/(?P<uidb36>[0-9A-Za-z]{1,13})-(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})/$",
        "password_reset_confirm",
        name="auth_password_reset_confirm"),

    url(r'^activate/complete/$',
        direct_to_template,
        {'template': 'registration/activation_complete.html'},
        name='registration_activation_complete'),
        # Activation keys get matched by \w+ instead of the more specific
        # [a-fA-F0-9]{40} because a bad activation key should still get to the view;
        # that way it can return a sensible "invalid key" message instead of a
        # confusing 404.
    url(r'^activate/(?P<activation_key>\w+)/$',
        activate,
        {'backend': 'account.backend.CommunityProfilesBackend'},
        name='registration_activate'),
    url(r'^register/$',
        register,
        {'backend': 'account.backend.CommunityProfilesBackend'},
        name='registration_register'),
    url(r'^register/complete/$',
        direct_to_template,
        {'template': 'registration/registration_complete.html'},
        name='registration_complete'),
    url(r'^register/closed/$',
        direct_to_template,
        {'template': 'registration/registration_closed.html'},
        name='registration_disallowed'),
)

