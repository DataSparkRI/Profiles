from tastypie.resources import Resource, ModelResource
from tastypie import fields, utils
from tastypie.cache import SimpleCache
from django.core.exceptions import ObjectDoesNotExist, MultipleObjectsReturned, ValidationError
from django.conf.urls.defaults import *
from maps.models import *
from profiles.models import GeoRecord, GeoLevel, Time, Indicator, Denominator, FlatValue
from django.contrib.gis.geos import Point
from profiles.utils import format_number
import json
from decimal import Decimal
from django.conf import settings
import HTMLParser
from geopy import geocoders

class PolygonMapFeatureResource(ModelResource):
    class Meta:
        resource_name= 'poly_feat' # layer features since they are all tied to the layer
        queryset = PolygonMapFeature.objects.all()
        allowed_methods = ['get']
        cache = SimpleCache(timeout=30)


class LineStringMapFeatureResource(ModelResource):
    class Meta:
        resource_name= 'ls_feat' # layer features since they are all tied to the layer
        queryset = LineStringMapFeature.objects.all()
        allowed_methods = ['get']
        cache = SimpleCache(timeout=30)


class PointMapFeatureResource(ModelResource):
    class Meta:
        resource_name= 'point_feat' # layer features since they are all tied to the layer
        queryset = PointMapFeature.objects.all()
        allowed_methods = ['get']
        cache = SimpleCache(timeout=30)


class GeoRecordResource(ModelResource):

    geom = fields.ListField()

    class Meta:
        resource_name = "geo"
        queryset = GeoRecord.objects.filter(level__in=GeoLevel.objects.filter(name__in=getattr(settings, 'DEFAULT_GEO_LEVELS')))
        allowed_methods = ['get']
        cache = SimpleCache(timeout=30)
        filtering = {
            'slug':('exact','in'),
        }
        excludes = ['geo_searchable']

    def get_multiple(self, request, **kwargs):
        """
        Returns a serialized list of resources based on the identifiers
        from the URL.

        Calls ``obj_get`` to fetch only the objects requested. This method
        only responds to HTTP GET.

        Should return a HttpResponse (200 OK).
        """
        self.method_check(request, allowed=['get'])
        self.is_authenticated(request)
        self.throttle_check(request)

        # Rip apart the list then iterate.
        kwarg_name = '%s_list' % self._meta.detail_uri_name
        obj_identifiers = kwargs.get(kwarg_name, '').split(';')
        objects = []
        not_found = []
        base_bundle = self.build_bundle(request=request)
        count = 0
        contains_suppressed_value = False
        sup_count = -1
        no_suppressed_value_list_idx = [] # we are gonna store the list index of values that are not immediately suppressed so we dont have to do a complete for loop
        for identifier in obj_identifiers:
            try:
                obj = self.obj_get(bundle=base_bundle, **{self._meta.detail_uri_name: identifier})
                bundle = self.build_bundle(obj=obj, request=request)
                bundle = self.full_dehydrate(bundle, for_list=True)
                try:
                    sup_count += 1
                    if bundle.data['geom']['properties']['value']['number'] == -1 and contains_suppressed_value == False:
                        contains_suppressed_value = True
                    # suppress all distribution if contains suppressed
                    if contains_suppressed_value and bundle.data['geom']['properties']['value']['type'] != 'change':
                        bundle.data['geom']['properties']['value']['percent'] = None
                        bundle.data['geom']['properties']['value']['f_percent'] = None
                    else:
                        no_suppressed_value_list_idx.append(sup_count)
                except KeyError:
                    # no data
                    pass
                # clean up a little bit
                try:
                    if count > 0:
                        del bundle.data['options'] # get rid of some silly cruft by adding some other cruft
                    count += 1
                except Exception as e:
                    pass

                objects.append(bundle)
            except ObjectDoesNotExist:
                not_found.append(identifier)


        # SUPP: Finally we need to clean up any data that wasnt imediately
        # suppressed.
        if contains_suppressed_value:
            for idx in no_suppressed_value_list_idx:
                objects[idx].data['geom']['properties']['value']['percent'] = None
                objects[idx].data['geom']['properties']['value']['f_percent'] = None

        # SUPP: At this point all the numbers that shouldnt be there should be gone.

        object_list = {
            self._meta.collection_name: objects,
        }
        try:
            options = objects[0].data['options']
            data_name = objects[0].data['geom']['properties']['value']['name']
            time_key = objects[0].data['geom']['properties']['value']['time']
            type_key = objects[0].data['geom']['properties']['value']['type']

            # we need to supress distributon
            if contains_suppressed_value:
                i_value_keys = {
                    'number':'#',
                }
            else:
                # NOTE: This is how we can get rid of Distribution showing up
                # in the indicator api
                #i_value_keys = options['vk']
                 i_value_keys = {
                    'number':'#',
                }

            if type_key == "i" and time_key != "change": # This is an indicator value
                value_keys = i_value_keys

            elif type_key == "i" and time_key == "change": #Change value
                value_keys = {
                    'percent': '%',
                }
                options = value_keys

            elif type_key == "d" and time_key != "change": # Denominator
                value_keys = {
                    'percent': '%',
                }
            else:
                value_keys = {}

            object_list['meta'] = {
                'name': "%s - %s" % (data_name, time_key),
                'time': time_key,
                'type':type_key,
                'options':options,
                'vk':value_keys,
            }


        except KeyError:
            # there are no options
            pass


        if len(not_found):
            object_list['not_found'] = not_found

        self.log_throttled_access(request)
        return self.create_response(request, object_list)

    def dehydrate_geom(self, bundle):
        union = bundle.request.GET.get('uni', None)

        if union is None:
            geoms = bundle.obj.get_geom(True) # default to merging them
        else:
            geoms = bundle.obj.get_geom(False)
        #NOTE: geoms returns a django.contrib.gis.geos.collections.MultiPolygon
        if geoms:
            all_geoms = json.loads(geoms.json)
            return all_geoms
        else:
            return {}

    def dehydrate(self, bundle):
        bundle.data['geom']['properties'] = {
                'label':bundle.obj.name,
                'slug':bundle.obj.slug,
                'level':{'slug':bundle.obj.level.slug, 'name':bundle.obj.level.name}
        }

        ### BY DEFAULT This resource just returns GeoRecords. If the request contains indicator info we can grab those too###
        if 'name' in bundle.request.GET:
            hp = HTMLParser.HTMLParser()
            # Grab indicator values and mush up the data.
            #<ind> can be id or slug
            #<time> is the name of a Time
            ind = None
            time = None
            nameQ = bundle.request.GET.get('name', None)
            timeQ = bundle.request.GET.get('time', None) # will default to a random available time
            try:
                nameQ = hp.unescape(nameQ.strip())

                if timeQ:
                    timeQ = timeQ.strip()

                if timeQ is not None:
                    data = FlatValue.objects.select_related().defer('indicator').get(display_title=nameQ, time_key=timeQ, geography=bundle.obj)
                else:
                    # get a random time
                    data = FlatValue.objects.select_related().filter(display_title=nameQ, geography=bundle.obj)[0]

                time_options = FlatValue.objects.filter(display_title=data.display_title, geography=data.geography).distinct('time_key').only('time_key')
                #related_options = FlatValue.objects.filter(indicator = data.indicator, geography=data.geography)\
                        #.distinct('display_title').exclude(display_title=data.display_title)
                bundle.data['geom']['properties']['value'] = data.to_dict()
                bundle.data['options'] = {
                    'times': [t.time_key for t in time_options],
                }
                vks = {'number': "#"}
                if data.indicator.display_percent and data.indicator.display_distribution:
                    vks['percent']="%"

                bundle.data['options']['vk'] = vks

            except FlatValue.DoesNotExist as e:
                bundle.data['geom']['properties']['value'] = {'error': 'Could Not find %s for Time %s and Geo: %s' % (nameQ, timeQ, bundle.obj.name) }

        return bundle

    def prepend_urls(self):
        return [
                url(r"^(?P<resource_name>%s)/(?P<slug>[\w\d_.-]+)/$" % self._meta.resource_name, self.wrap_view('dispatch_detail'), name="api_dispatch_detail"),
        ]

class GeoCoder(object):
    def geocode_address_google(self, street, city, zip_code=''):
        address = "%s %s %s" % (street, city, zip_code)
        results = []
        google = geocoders.GoogleV3()
        try:
            place, geocode = google.geocode(address)
            results.append({'address':place,
                            'lat':geocode[0],
                            'lng':geocode[1]
                           })
        except Exception as e:
            # Found more than one
            for r in google.doc['results']:
                d = r['geometry']['location'].copy()
                d['address'] = r['formatted_address']
                results.append(d)

        return results

    def geocode_address_dotus(self, street, city, zip_code='', state=None):
        """ NOTE: This geocoder is particular about having a state"""
        if state:
            state = ", " + state
        else:
            state = ""
        address = "%s,  %s, %s" % (street, city, state)
        us = geocoders.GeocoderDotUS(format_string="%s")
        results = []
        try:
            place, (lat, lng) = us.geocode(address)

            results.append({'address':place,
                            'lat':lat,
                            'lng':lng})
        except Exception as e:
            pass

        return results

    def geocode_address(self, street, city, zip_code=''):
        result = self.geocode_address_dotus(street, city, zip_code)
        if len(result) == 0:
            result = self.geocode_address_google(street, city, zip_code)

        return result

    def __init__(self, street='', city='', zip_code=''):
        self.results = []
        self.status = None
        self.raw_address = ''
        if street != '':
            if street != '':
                self.raw_address += street
            if city != '':
                self.raw_address += ',' + city
            if zip_code != '':
                self.raw_address += ',' + zip_code

            geo_result = self.geocode_address(street, city, zip_code)
            if geo_result:
                self.status = 'success'
                used_addresses = []
                for result in geo_result:
                    d = {}
                    GEOS_point = Point(float(result['lng']), float(result['lat']))
                    try:
                        if result['address'] not in used_addresses:
                            sfs = PolygonMapFeature.objects.filter(geom__contains=GEOS_point).only('geo_key', 'geo_level')
                            d['geography'] = []
                            for s in sfs:
                                # we essentially link over these polys to a
                                # georecord
                                try:
                                    rec = GeoRecord.objects.get(geo_id=s.geo_key, level__id = s.geo_level, geo_searchable=True)
                                except GeoRecord.MultipleObjectsReturned:
                                    rec = GeoRecord.objects.filter(geo_id=s.geo_key, level__id = s.geo_level, geo_searchable=True)[0]

                                d['geography'].append({
                                        'name':rec.name,
                                        'slug':rec.slug,
                                        'level':{
                                            'name':rec.level.name,
                                            'slug':rec.level.slug,
                                        }

                                })

                            d['location'] = {
                                'address': result['address'],
                                'lat': result['lat'],
                                'lng': result['lng'],
                            }

                            used_addresses.append(result['address'])
                            self.results.append(d)
                        else:
                            pass

                    except GeoRecord.DoesNotExist:
                        pass
                        #self.results.append(d)
            else:
                self.status = 'fail'
                self.results = []
        else:
            self.status = 'invalid'
            self.results = []


class GeoCodeResource(Resource):
    status = fields.CharField(attribute='status')
    raw_address = fields.CharField(attribute='raw_address')
    results = fields.ListField(attribute='results', blank=True)

    class Meta:
        resource_name = 'geocode'
        object_class = GeoCoder

    def detail_uri_kwargs(self, bundle_or_obj):
        kwargs = {}
        return kwargs

    def get_object_list(self, request):
        results = []
        street = request.GET.get('street', '')
        city = request.GET.get('city', '')
        zip_code = request.GET.get('zip','')
        gc = GeoCoder(street, city, zip_code)
        results.append(gc)
        return results

    def obj_get_list(self, bundle, **kwargs):
        return self.get_object_list(bundle.request)

    def obj_get(self, request=None, **kwargs):
        pass

    def obj_create(self, bundle, request=None, **kwargs):
        pass

    def obj_update(self, bundle, request=None, **kwargs):
        pass

    def obj_delete_list(self, request=None, **kwargs):
        pass

    def obj_delete(self, request=None, **kwargs):
        pass

    def rollback(self, bundles):
        pass
