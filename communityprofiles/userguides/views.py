from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
# Create your views here.
from profiles.models import GeoLevel, GeoRecord, DataDomain
from userguides.models import AboutTopic
from userguides.models import faq as FAQ
def about(request):
    geo_record, indicator = None, None
    from maps.models import Setting
    setting = Setting.objects.filter(active=True);
    geo_record = GeoRecord.objects.get(id=setting[0].DEFAULT_GEO_RECORD_ID)
    
    if len(setting) == 0:
       raise ImproperlyConfigured('DEFAULT_GEO_RECORD_ID must be defined')
    ctx ={
            'geo_record': geo_record,
            'topics': AboutTopic.objects.filter(published=True).order_by("display_order")
        }
    return render_to_response('userguides/about.html', ctx, context_instance=RequestContext(request))

def faq(request):
    geo_record, indicator = None, None
    from maps.models import Setting
    setting = Setting.objects.filter(active=True);
    geo_record = GeoRecord.objects.get(id=setting[0].DEFAULT_GEO_RECORD_ID)


    if len(setting) == 0:
       raise ImproperlyConfigured('DEFAULT_GEO_RECORD_ID must be defined')
    ctx ={
            'geo_record': geo_record,
            'faqs': FAQ.objects.filter(published=True).order_by("display_order")
        }
    return render_to_response('userguides/faq.html', ctx, context_instance=RequestContext(request))
