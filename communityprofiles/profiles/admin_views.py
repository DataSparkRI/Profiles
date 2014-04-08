from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from django.utils import simplejson as json
from django.db.models import Q
from django.conf import settings
from profiles.models import *
from profiles.utils import *
from profiles.tasks import generate_indicator_data
from django.contrib.sites.models import Site


@user_passes_test(lambda u:u.is_staff)
def admin_preview(request):
    """ This view should get passed an indicator id via the django admin """
    # check for required parameters
    if 'i' not in request.GET:
        raise Http404('Bad Request -- Indicator is required')

    indicator = get_object_or_404(Indicator, id=request.GET.get('i'))
    context = {
            'indicator':indicator
            }

    return render_to_response('admin/admin_preview.html',context, context_instance=RequestContext(request))

@user_passes_test(lambda u:u.is_staff)
def raw_indicator_json(request):
    """
        This view should only be assessible to staff. It exposes raw access to indicators values from the db.
        It returns the values that Profiles gets when you generate data.
        In order to conserve resources, we'll only allow one indicator and one geography at a time.
    """
    # check for required parameters
    if 'i' not in request.GET:
        return HttpResponse(json.dumps({'error':'Bad Request -- Indicator is required'}))
    if 'r' not in request.GET:
        return HttpResponse(json.dumps({'error':'Bad Request -- GeoRecord is required'}))

    ind_id = request.GET.get('i')
    rec_id = request.GET.get('r')

    indicator = get_object_or_404(Indicator, id=int(ind_id))

    try:
        geo_record = GeoRecord.objects.get(id=int(rec_id))
        results = indicator.collect_data(geo_record)
    except GeoRecord.DoesNotExist:
        return HttpResponse(json.dumps({'error':'No GeoRecord with that Id'}))

    return HttpResponse(json.dumps(results), mimetype="application/json")

@user_passes_test(lambda u:u.is_staff)
def indicator_action(request, indicator_id):
    """ kicks of celery tasks on an indicator"""

    next_url = request.GET.get('next') or '/admin'

    try:
        indicator = Indicator.objects.get(pk=int(indicator_id))
        generate_indicator_data.delay(indicator)
    except Indicator.DoesNotExist:
        pass
    return redirect(next_url)

