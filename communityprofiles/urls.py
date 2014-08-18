import os
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response
from django.contrib import admin
admin.autodiscover()
from profiles.views import search as profiles_search
from views import front_page
from tastypie.api import Api
from maps.api import *
from profiles.api import *

maps_api = Api(api_name='v1')
maps_api.register(PolygonMapFeatureResource())
maps_api.register(LineStringMapFeatureResource())
maps_api.register(PointMapFeatureResource())
maps_api.register(GeoRecordResource())
maps_api.register(GeoCodeResource())

data_api=Api(api_name='v1')
data_api.register(IndicatorResource())

urlpatterns = patterns('',
    (r'^api/',include(data_api.urls)),
    (r'^about/',include('userguides.urls')),
    url(r'^radmin/', include('radmin.urls')),
    (r'^admin/', include(admin.site.urls)),
    (r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': os.path.join(os.path.dirname(__file__), 'media')}),
    #(r'^account/', include('account.urls')),
    (r'^profiles/', include('profiles.urls')),
    (r'^census/', include('census.urls')),
    #(r'^sentry/', include('sentry.urls')),
    url(r'^search/$', profiles_search, name='profiles_search'),
    url(r'^$', front_page, name='front_page'),
    (r'^maps_api/', include(maps_api.urls)), # ex: /maps_api/v1/l_feat/307/?format=json
)
