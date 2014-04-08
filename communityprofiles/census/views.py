
import urllib2
from django.shortcuts import render
from django.http import HttpResponse
# Create your views here.
from django.shortcuts import render_to_response
from django.template import RequestContext
def tables_xml(request, dataset):
    if dataset == '2000sf1':
        url = 'http://www.census.gov/developers/data/2000_sf1.xml'
    elif dataset == '2000sf3':
        url = 'http://www.census.gov/developers/data/2000_sf3.xml'
    elif dataset =='2010sf1':
        url = 'http://www.census.gov/developers/data/sf1.xml'
    elif dataset =='acs5yr2010':
        url = 'http://www.census.gov/developers/data/acs_5yr_2010_var.xml'
    elif dataset =='acs5yr2011':
        url = 'http://www.census.gov/developers/data/acs_5yr_2011_var.xml'
    else:
        #default
        url = 'http://www.census.gov/developers/data/2000_sf1.xml'

    result = urllib2.urlopen(url).read()
    return HttpResponse(result ,content_type="application/xml")
    
def variable_tool(request):

   return render_to_response('census/variable_tool.html',
                              context_instance=RequestContext(request))
