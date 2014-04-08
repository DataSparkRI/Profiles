from django.conf.urls.defaults import *
from tastypie.resources import Resource, ModelResource
from tastypie.exceptions import NotFound, BadRequest, InvalidFilterError, HydrationError, InvalidSortError, ImmediateHttpResponse
from tastypie import fields
from profiles.models import *
from choropleth import breaks_from_dataset
from profiles.utils import get_default_levels

class IndicatorResource(ModelResource):

    class Meta:
        queryset = Indicator.objects.filter(published=True)
        resource_name = 'ind'
        allowed_methods = ['get']
        filtering = {
            'slug':('exact','in'),
        }
        excludes = ['display_change', 'display_distribution', 'display_percent', 'last_generated_at','published']

    def __init__(self):
        levels = get_default_levels()
        self.valid_levels = GeoLevel.objects.filter(name__in=levels)
        super(IndicatorResource, self).__init__()

    def dehydrate(self, bundle):
        """ Customized dehydrate that returns indicator values for Geography"""
        ind = bundle.obj
        times = ind.get_times()
        bundle.data['times'] = times

        if 'geo' in bundle.request.GET:
            q_times = None # times via query
            if 'time' in bundle.request.GET:
                try:
                    q_times = Time.objects.filter(name=bundle.request.GET.get('time'))
                except Time.DoesNotExist:
                    pass
            denoms = ind.denominator_set.all()
            # get the list of geos, they can be a slug or an id
            geo_list = bundle.request.GET.getlist('geo')
            # we need to clean up the geo list
            c_geo_list = []
            geos = []

            for gq in geo_list:
                rec = None
                try:
                    id = int(gq)
                    try:
                        rec = GeoRecord.objects.get(pk=id, level__in=self.valid_levels)
                    except GeoRecord.DoesNotExist:
                        pass
                except ValueError:
                    try:
                        rec = GeoRecord.objects.get(slug=gq, level__in=self.valid_levels)
                    except GeoRecord.DoesNotExist:
                        pass
                if rec is not None and rec not in geos:
                    geos.append(rec)
            # we need to return values for this indicator now
            ind_values = {}

            for g in geos:
                ind_values[g.name] = ind.get_values_as_dict(g, q_times)

            # Finally return the structure
            if len(geos) > 1:
                ind_values['natural_breaks'] = breaks_from_dataset(ind_values, times)
            bundle.data['data'] = ind_values

        return bundle

    def prepend_urls(self):
        return [
                url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
            ]

