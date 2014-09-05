from django.shortcuts import render
from django.shortcuts import render_to_response, get_object_or_404
from django.template import RequestContext
# Create your views here.
from profiles.models import GeoLevel, GeoRecord, DataDomain
from userguides.models import AboutTopic, StayInTouchUser
from userguides.models import faq as FAQ
from django.http import HttpResponse
import json

def stay(request):
    if request.method == 'GET':
       response_data = {}
       response_data['result'] = 'failed'
       response_data['message'] = 'Must be POST request'
       return HttpResponse(json.dumps(response_data), content_type="application/json")
    elif request.method == 'POST':
       first_name = request.POST["first_name"]
       last_name = request.POST["last_name"]
       email = request.POST["mail"]
       result = StayInTouchUser.objects.filter(email=email)
       response_data = {'result':'success'} 
       if len(result) == 0: # one email can only reg once
          StayInTouchUser(email=email, first_name=first_name, last_name=last_name).save()
          response_data.update({'message':'Thank you for stay in touch'})
       else:
          response_data.update({'message':'Your email is already in the system. Thank you for stay in touch.'})
       return HttpResponse(json.dumps(response_data), content_type="application/json")

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
