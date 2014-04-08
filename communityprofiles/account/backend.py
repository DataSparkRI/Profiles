from registration.backends.default import DefaultBackend
from account.forms import RegistrationForm

class CommunityProfilesBackend(DefaultBackend):
    def register(self, request, **kwargs):
        new_user = super(CommunityProfilesBackend, self).register(request, **kwargs)
        new_user.first_name = kwargs['first_name']
        new_user.last_name = kwargs['last_name']
        new_user.save()
        
        profile = new_user.get_profile()
        for k, v in kwargs.items():
            if k in ('username', 'first_name', 'last_name', 'email', 'password1', 'password2'):
                continue
            setattr(profile, k, v)
        profile.save()
        return new_user

    def get_form_class(self, request):
        return RegistrationForm
