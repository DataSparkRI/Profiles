from django.http import Http404, HttpResponse, HttpResponseBadRequest
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.template import RequestContext
from data_displays.models import DataDisplay
from profiles.models import GeoRecord


def index(request):
	return HttpResponse("<h1>Hello there</h1>")

def data_display(request, datadisplay_slug):
    data_display = get_object_or_404(DataDisplay, slug=datadisplay_slug)

    display_template = data_display.template

    visualizations = display_template.visualizations.all()

    css_resources = []
    js_resources = []

    #collect visualization_resources
    for vis in visualizations:
        css_resources.extend(vis.get_css_resources())
        js_resources.extend(vis.get_js_resources())

    #remove any duplicates from the list if we have mulitple visulizations that share resources
    css_resources = remove_dupes(css_resources)
    js_resources = remove_dupes(js_resources)

    indicators = {}
    for ind in display_template.indicators.all():
        indicators[ind.slug] = {
            'display_name': ind.display_name,
            'display_change':ind.display_change,
            'display_distribution':ind.display_distribution,
            'slug':ind.slug,
            'id': ind.pk,
            'denominators': [{'label':d.label, 'id':d.id} for d in ind.denominator_set.all()],
            'times': ind.get_times()
        }

    ctx = {
			'display':data_display,
			'css':css_resources,
			'js':js_resources,
			'geo_record' : data_display.record.id,
			'indicator_ids':','.join([str(indicators[i]['id']) for i in indicators]),
            'indicators': indicators
    }

    """Get geo records with this record as its parent --- how about calling it... geo_children?
        but only if we are the State or Municipality level
    """

    if any(k in data_display.record.level.name for k in ['State','state','municipality','Municipality']):
        ctx['records'] = GeoRecord.objects.filter(parent=data_display.record)
    else:
        ctx['records'] = [data_display.record]

    return render_to_response('data_displays/base.html', ctx, context_instance=RequestContext(request))


#http://www.peterbe.com/plog/uniqifiers-benchmark
def remove_dupes(seq, idfun=None):
   # order preserving
   if idfun is None:
       def idfun(x): return x
   seen = {}
   result = []
   for item in seq:
       marker = idfun(item)
       # in old Python versions:
       # if seen.has_key(marker)
       # but in new ones:
       if marker in seen: continue
       seen[marker] = 1
       result.append(item)
   return result





