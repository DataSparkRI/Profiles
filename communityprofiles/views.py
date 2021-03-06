from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.shortcuts import redirect

from profiles.models import GeoRecord
from maps.models import Setting

def front_page(request):
    setting = Setting.objects.filter(active=True);
    if len(setting) == 0:
       raise ImproperlyConfigured('DEFAULT_GEO_RECORD_ID must be defined')
    """ Community Profiles front page.

    This view redirects to the default geography. If none is configured, an
    exception will be raised.
    """
    #if not hasattr(settings, 'DEFAULT_GEO_RECORD_ID'):
    #    raise ImproperlyConfigured('DEFAULT_GEO_RECORD_ID must be defined')
    record = GeoRecord.objects.get(id=setting[0].DEFAULT_GEO_RECORD_ID)

    return redirect(record.get_absolute_url())
