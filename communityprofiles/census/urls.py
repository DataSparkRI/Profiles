from django.conf.urls import patterns, include, url
urlpatterns = patterns('',
    url(r'^api_tables/(?P<dataset>[a-z0-9]+)/$', 'census.views.tables_xml', name='api_tables'),
    url(r'^variable_tool/$','census.views.variable_tool', name='tool'),
)
