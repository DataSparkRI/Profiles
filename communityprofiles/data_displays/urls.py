
from django.conf.urls.defaults import *
from django.shortcuts import render_to_response


urlpatterns = patterns('data_displays.views',
   url(r'^$','index'),
   url(r'^(?P<datadisplay_slug>[-\w]+)$', 'data_display', name='data_display'),
)
