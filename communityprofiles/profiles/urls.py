from django.conf.urls.defaults import *

urlpatterns = patterns('',
    url(r'^data_display/', include('data_displays.urls')),
    url(r'^dataview/(?P<level_slug>[-\w]+)/(?P<geo_slug>[-\w]+)/(?P<indicator_slug>[-\w]+)/$', 'profiles.views.data_view', name='data_view'),
	url(r'^indicator/info/$', 'profiles.views.indicator_info', name='indicator_info'),
	url(r'^indicator_data/multi/$', 'profiles.views.multi_indicator_json', name='multi_indicator_json'),
    url(r'^api/geo/$','profiles.views.geography_list_json', name='geo_api'),
    url(r'^api/raw/$','profiles.admin_views.raw_indicator_json', name='raw_indicator_json'),
    url(r'^geojson/$', 'profiles.views.geojson', name='geojson'),
    url(r'^preview/$','profiles.admin_views.admin_preview', name='admin_preview'),
    url(r'^export/$', 'profiles.views.export_csv', name='export_csv'),
    url(r'^i_a/(?P<indicator_id>[\d]+)/$', 'profiles.admin_views.indicator_action', name="indicator_action"),
    url(r'^(?P<geo_level_slug>[-\w]+)/(?P<geo_record_slug>[-\w]+)/(?P<data_domain_slug>[-\w]+)/(?P<indicator_slug>[-\w]+)/$',
        'profiles.views.indicator', name='indicator'),
    url(r'^(?P<geo_level_slug>[-\w]+)/(?P<geo_record_slug>[-\w]+)/(?P<data_domain_slug>[-\w]+)/$', 'profiles.views.data_domain', name='data_domain'),
    url(r'^(?P<geo_level_slug>[-\w]+)/(?P<geo_record_slug>[-\w]+)/$', 'profiles.views.geo_record', name='geo_record'),
    url(r'^(?P<geo_level_slug>[-\w]+)/$', 'profiles.views.geo_level', name='geo_level'),
)
