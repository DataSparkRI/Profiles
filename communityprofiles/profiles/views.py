from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import render_to_response, get_object_or_404, redirect
from django.http import Http404, HttpResponse
from django.template import RequestContext
from django.utils import simplejson as json
from django.db.models import Q
from django.conf import settings
from haystack.query import SearchQuerySet
from haystack.forms import ModelSearchForm
from profiles.models import GeoLevel, GeoRecord, DataDomain, Indicator, \
                            IndicatorPart, FlatValue, \
                            DataSource, Time, Value, DataPoint,Denominator
from profiles.map import geo_record_map, indicator_map
from profiles.tasks import generate_indicator_data
from choropleth import classes_and_colors
from profiles.utils import *
from data_displays.models import DataDisplay
from django.contrib.sites.models import Site
import urllib
import json
import zipfile, csv, StringIO
from geopy import geocoders
from django.contrib.gis.geos import fromstr
from maps.models import *


def geo_level(request, geo_level_slug):
    """ Overview for a geo level. """
    level = get_object_or_404(GeoLevel, slug=geo_level_slug)
    return render_to_response('profiles/geo_level.html', {'geo_level': level,},
        context_instance=RequestContext(request))

def geo_record(request, geo_level_slug, geo_record_slug):
    """ Profile view for a geo record. Displays defualt indicators """
    return redirect('data_domain', geo_level_slug=geo_level_slug, geo_record_slug=geo_record_slug, data_domain_slug='overview')


def data_domain(request, geo_level_slug, geo_record_slug, data_domain_slug):
    """ Overview of a data domain for a geo record """
    level = get_object_or_404(GeoLevel, slug=geo_level_slug)

    try:
        record = GeoRecord.objects.defer('mappings', 'components', 'parent').get(level=level, slug=geo_record_slug)
    except GeoRecord.DoesNotExist:
        raise Http404

    filter_key = ''
    if level.related_within:
        geoids = json.loads(record.geo_id_segments)
        sum_lev = level.related_within.summary_level
        filter_key = geoids[sum_lev]

    domain = get_object_or_404(DataDomain, slug=data_domain_slug)
    #indicators = domain.indicators.filter(published=True, levels__in=[level])
    levels = get_levels_as_list()

    if not request.GET or request.GET.get('e'):
        return render_to_response('profiles/data_domain.html',
            {
                'geo_level': level,
                'geo_record': record,
                'data_domain': domain,
                'level_json':json.dumps({'id':level.id, 'name':level.lev_name, 'slug':level.slug, 'sumlev':level.summary_level}),
                'levels': json.dumps(levels),
                'rec_json':json.dumps({'id':record.id, 'name': record.name, 'slug':record.slug, 'geom_id':record.get_geom_id(), 'geo_id':record.geo_id}),
                'filter_key': filter_key,
             },
            context_instance=RequestContext(request))
    else:

        lng = request.GET.get('lng')
        lat = request.GET.get('lat')
        place = request.GET.get('place')
        GEOS_point = fromstr("POINT(%s %s)" % (lng, lat))

        return render_to_response('profiles/data_domain.html',
            {
             'geo_level': level,
             'geo_record': record,
             'data_domain': domain,
             'indicators': indicators
             },
            context_instance=RequestContext(request))


def data_view(request, level_slug, geo_slug, indicator_slug):
    """ View a indicator in some sort of data display """
    try:
        record = GeoRecord.objects.defer('mappings', 'components', 'parent').get(level__slug=level_slug, slug=geo_slug)
    except GeoRecord.DoesNotExist:
        raise Http404

    denom = request.GET.get('d', None)
    value_key = 'number'
    # BELOW we are using the term indicator interchangably with denominator.
    if not denom:
        try:
            indicator = Indicator.objects.get(slug=indicator_slug)
        except Indicator.DoesNotExist:
            raise Http404
    else:
        # displaying a denominator
        try:
            indicator = Denominator.objects.get(slug=indicator_slug)
            value_key = "percent"
        except Denominator.DoesNotExist:
            raise Http404


    levels = get_indicator_levels_as_list(indicator)
    level = record.level
    display_options = indicator.get_display_options()

    ctx = {
        'geo_record':record,
        'indicator': indicator,
        'times': json.dumps(indicator.get_times(True)),
        'levels': json.dumps(levels),
        'level_json':json.dumps({'id':level.id, 'name':level.lev_name, 'slug':level.slug, 'sumlev':level.summary_level}),
        'rec_json':json.dumps({'id':record.id, 'name': record.name, 'slug':record.slug, 'geom_id':record.get_geom_id(), 'geo_id':record.geo_id}),
        'display_options':json.dumps(display_options),
        'value_key':value_key,
    }

    is_status = "status" in request.GET
    if is_status:
        ctx.update({'print':True})
        #return render_to_response('profiles/dataprint.html', ctx, context_instance=RequestContext(request))
    else:
        ctx.update({'print':False})
    return render_to_response('profiles/dataview.html', ctx, context_instance=RequestContext(request))

def indicator_info(request):
    """ return indicator meta data """
    slug = request.GET.get('s', None)
    if slug is None:
        raise Http404('Sorry, we couldnt find the indicator your requested.')
    try:
        indicator = Indicator.objects.get(slug=slug, published = True)
    except Indicator.DoesNotExist:
        raise Http404('Sorry, we couldnt find the indicator your requested.')
    notes = indicator.get_notes()
    return render_to_response('profiles/notes.html', {'notes':notes, 'indicator':indicator}, context_instance=RequestContext(request))



def indicator(request, geo_level_slug, geo_record_slug, data_domain_slug, indicator_slug):
    """ Single-indicator view. Context is geo record and data domain
    """
    level = get_object_or_404(GeoLevel, slug=geo_level_slug)
    try:
        record = GeoRecord.objects.defer('mappings', 'components', 'parent').get(level=level, slug=geo_record_slug)
    except GeoRecord.DoesNotExist:
        raise Http404
    domain = get_object_or_404(DataDomain, slug=data_domain_slug)

    try:
        indicator = domain.indicators.get(slug=indicator_slug, published=True)
    except Indicator.DoesNotExist:
        raise Http404('Sorry, we couldnt find the indicator your requested.')

    time = None

    time_name= request.GET.get('time', None)

    value_key = request.GET.get('vk', None) # this is the value key coming from map controls

    map_layers = get_layers_for_geo(record)

    m_times = indicator.get_times(True)

    display_options = indicator.get_display_options()

    related_options = FlatValue.objects.filter(indicator = indicator, geography=record)\
            .distinct('display_title').exclude(display_title=indicator.display_name).only('display_title')

    related_opts_list = [r.display_title for r in related_options]

    ctx = {'geo_level': level,
           'geo_record': record,
           'data_domain': domain,
           'indicator': indicator,
           'map_layers':map_layers,
           'm_times':json.dumps(m_times),
           'related':json.dumps(related_opts_list),
           'display_options':json.dumps(display_options),
    }

    #finally we need to check we are requesting a printable version
    render = request.GET.get('render', None)

    if render == 'print':
        return render_to_response('profiles/indicator_print.html', ctx, context_instance=RequestContext(request))

    return render_to_response('profiles/indicator.html',ctx, context_instance=RequestContext(request))

"""
def indicator_old(request, geo_level_slug, geo_record_slug, data_domain_slug, indicator_slug):
    #Single-indicator view. Context is geo record and data domain
    level = get_object_or_404(GeoLevel, slug=geo_level_slug)
    record = get_object_or_404(GeoRecord, level=level, slug=geo_record_slug)
    domain = get_object_or_404(DataDomain, slug=data_domain_slug)
    map_layers = get_layers_for_geo(record)

    try:
        indicator = domain.indicators.get(slug=indicator_slug, published=True)
    except Indicator.DoesNotExist:
        raise Http404('Sorry, we couldnt find the indicator your requested.')

    if not request.GET or request.GET.get('e'):
        return render_to_response('profiles/indicator.html',
            {'geo_level': level, 'geo_record': record, 'data_domain': domain,
                'indicator': indicator, 'map_layers':map_layers, 'beta':settings.BETA
            },
            context_instance=RequestContext(request))
    else:
        lng = request.GET.get('lng')
        lat = request.GET.get('lat')
        place = request.GET.get('place')
        GEOS_point = fromstr("POINT(%s %s)" % (lng, lat))
        return render_to_response('profiles/indicator.html',
            {'geo_level': level, 'geo_record': record, 'data_domain': domain,
                'indicator': indicator,
                'gmap': indicator_map(indicator, record, domain, GEOS_point, place),
                'beta':settings.BETA
            },
            context_instance=RequestContext(request))
"""

#-------------------------------------------------------------------------

def data_display(request, datadisplay_slug):
    data_display = get_object_or_404(DataDisplay, slug=datadisplay_slug)
    return HttpResponse(data_display.html)

#-------------------------------------------------------------------------
# API
#-------------------------------------------------------------------------

def geography_list_json(request):
    """
        API access for geography related things
        Usage:
            <param> l: Geography Level. Can be one of the following: state, municipalities, tracts.
            <param> name: If name is set, param l is ignored. Find a geography by name.
            <param> show_mappings: Boolean, shows all mappings for this geography. Default to False
            <param> depth: How many child geos are shown. all or 1 Default None
    """
    #Check for required params
    if 'l' not in request.GET and 'name' not in request.GET:
        raise Http404('Bad Request -- Level or Name is required ex: ?l=state or ?name=providence')

    if 'l' in request.GET and 'name' in request.GET:
        raise Http404('Bad Request -- Level and Name cannot both be used: ?l=state or ?name=providence')

    level = None
    geo_level = None
    depth = request.GET.get('depth', '0')
    show_mappings = request.GET.get('show_mappings', False)
    levels = GeoLevel.objects.filter(slug__in=['state','municipality','census-tract'])
    results = {}

    # Check for level
    if 'l' in request.GET:
        level = request.GET.get('l')
        if level in ['state','municipality','census-tract']:
            geo_level = get_object_or_404(GeoLevel, slug=level)
            # get records for level
            records = GeoRecord.objects.filter(level=geo_level).order_by('-name')
            for rec in records:
                if rec.name not in results:
                    results[rec.name] = rec.get_as_dict()

                    # include mapped geos but only if not census-tract?
                    if level != 'census-tract':
                        if show_mappings != False:
                            results[rec.name]['mappings'] = []
                            for mapped in rec.mappings.all():
                                results[rec.name]['mappings'].append(mapped.get_as_dict())

                    #depth
                    if depth != '0':
                        results[rec.name]['children'] = []
                        if depth == '1':
                            # show the children
                            for child in rec.child_records():
                                results[rec.name]['children'].append(child.get_as_dict())

        else:
            raise Http404('Bad Request --%s is not a valid Level. Use state, municipality or census-tract' % level)

    if 'name' in request.GET:
        name = request.GET.get('name')
        rec  = get_object_or_404(GeoRecord, level__in=levels, name=name)
        if rec.name not in results:
            results[rec.name] = rec.get_as_dict()

            # include mapped geos. Getting mappings for census-tract works here?
            if show_mappings != False:
                results[rec.name]['mappings'] = []
                for mapped in rec.mappings.all():
                    results[rec.name]['mappings'].append(mapped.get_as_dict())

            #depth
            if depth != '0':
                results[rec.name]['children'] = []
                if depth == '1':
                    # show the children
                    for child in rec.child_records():
                        results[rec.name]['children'].append(child.get_as_dict())

    return HttpResponse(json.dumps(results), mimetype="application/json")

def multi_indicator_json(request):
    """ The main API from which data displays get data"""
    indicators = None
    geo_records = None
    times = None
    results = {}

    if 'i' in request.GET:
        indicators = request.GET.getlist('i')
    else:
        raise Http404('Bad Request -- Indicator is required')

    if 'record' in request.GET:
        geo_records = request.GET.getlist('record')
    elif 'level' in request.GET:
        level = get_object_or_404(GeoLevel, id=int(request.GET['level']))
        geo_records = [g['id'] for g in GeoRecord.objects.values('id').filter(level=level)]
    else:
        raise Http404('Bad Request -- Geo Record is required')

    if 'time' in request.GET:
        times=[t.id for t in Time.objects.filter(name__in=request.GET.getlist('time'))]
    else:
        times = []

    for ind_id in indicators:
        try:
            indicator = Indicator.objects.get(pk=ind_id, published=True)
            results[indicator.id] = {
                'indicator':{
                    'id':indicator.id,
                    'display_name': indicator.display_name,
                    'name':indicator.name,
                    'slug':indicator.slug,
                    'display_distribution':indicator.display_distribution
                },
                'data':[],
            }
            for geo_id in geo_records:
                try:
                    rec = GeoRecord.objects.get(pk=geo_id)
                    ind_info = indicator.get_indicator_info(rec, times)

                    formated_data_source = {
                            'key':rec.geo_id,
                            'level': rec.level.name,
                            'label': rec.name,
                            'datatype':indicator.data_type,
                            'distribution' : {}

                    }

                    # split by times using above
                    for t in ind_info['indicator_times']:
                        value = ind_info['values'][t.id]
                        formated_data = formated_data_source.copy()
                        formated_data['time'] = t.name
                        formated_data['value'] = float(value.number) if value and value.number else 0
                        formated_data['f_value']= format_number(float(value.number) if value and value.number else 0, indicator.data_type)
                        formated_data['moe'] = float(value.moe) if value and value.moe else 0
                        formated_data['f_moe']= format_number(float(value.moe) if value and value.moe else 0, indicator.data_type)
                        try:
                            if ind_info['distribution'][t.id]:
                                formated_data['distribution']['f_number'] = format_number(float(ind_info['distribution'][t.id].number) if ind_info['distribution'][t.id].number else None, indicator.data_type)
                                formated_data['distribution']['f_percent'] = format_number(float(ind_info['distribution'][t.id].percent) if ind_info['distribution'][t.id].percent else None, "PERCENT")
                                formated_data['distribution']['number'] = float(ind_info['distribution'][t.id].number) if ind_info['distribution'][t.id].number else None
                                formated_data['distribution']['percent'] = float(ind_info['distribution'][t.id].percent) if ind_info['distribution'][t.id].percent else None
                            else:
                                formated_data['distribution']['f_number'] = 0
                                formated_data['distribution']['f_percent'] = 0
                                formated_data['distribution']['number'] = 0
                                formated_data['distribution']['percent'] = 0

                        except KeyError:
                            formated_data['distribution']['f_number'] = 0
                            formated_data['distribution']['f_percent'] = 0
                            formated_data['distribution']['number'] = 0
                            formated_data['distribution']['percent'] = 0
                        # change only appears when multi years are selected
                        if ind_info['change']:
                            formated_data['change_number'] = format_number(float(ind_info['change'].number) if ind_info['change'].number else 0, indicator.data_type)
                            formated_data['f_change_number'] = float(ind_info['change'].number) if ind_info['change'].number else 0
                            formated_data['f_change_percent'] = format_number(float(ind_info['change'].percent) if ind_info['change'].percent else 0, "PERCENT")
                            formated_data['change_percent'] = float(ind_info['change'].percent) if ind_info['change'].percent else 0

                        formated_data['denominators'] = {}
                        # get the denominators
                        for denom in ind_info['denominators']:
                            denom_value = denom['values'][t.id]
                            formated_data['denominators'][denom['denominator'].label] = {
                                'percent': float(denom_value.percent) if denom_value and denom_value.percent else 0,
                                'moe': float(denom_value.moe) if denom_value and denom_value.moe else 0,
                                'value': float(denom_value.number) if denom_value and denom_value.number else 0,
                                'f_value': format_number(float(denom_value.number) if denom_value and denom_value.number else 0)

                            }

                        results[indicator.id]['data'].append(formated_data)

                except GeoRecord.DoesNotExist:
                    continue

            # the natural breaks
            all_classes = {}
            result = results[indicator.id]['data']

            # natual breaks for denoms
            # grab all the denom keys
            denoms_in_indicator = [ denom for denom in results[indicator.id]['data'][0]['denominators'] ]
            denom_vals = {}

            for d_key in denoms_in_indicator:
                denom_vals[d_key] = []

            for r in result:
                # We are now iterating through all the data records broken up by geos
                # get classes and colors for indicator value
                classes, colors = classes_and_colors(map(lambda r: r['value'], result))

                classes = map(
                    lambda c: {'min': float(c[0]), 'f_min':format_number(float(c[0]),result[0]['datatype']),'max': float(c[1]),'f_max':format_number(float(c[1]),result[0]['datatype']),'datatype':result[0]['datatype']},
                classes
                    )

                all_classes[r['time']] = classes

                # distribution natural breaks
                distro_classes, colors = classes_and_colors( map(lambda r: r['distribution']['percent'] if r['distribution']['percent'] is not None else 0, result) )

                distro_classes = map(
                    lambda c: {'min': float(c[0]), 'f_min':format_number(float(c[0]),result[0]['datatype']),'max': float(c[1]),'f_max':format_number(float(c[1]),result[0]['datatype']),'datatype':result[0]['datatype']}, distro_classes)
                all_classes[r['time'] + "_" + "distribution"] = distro_classes

                for denom_key in r['denominators']:
                    denom = r['denominators'][denom_key]
                    denom_vals[denom_key].append(denom['percent'])

                    # At this point we've collected all the values from the denoms into 2 lists
                    denom_classes, colors = classes_and_colors(denom_vals[denom_key])
                    denom_classes = map(lambda c: {'min': float(c[0]), 'f_min':format_number(float(c[0]),result[0]['datatype']),'max': float(c[1]),'f_max':format_number(float(c[1]),result[0]['datatype']),'datatype':result[0]['datatype']}, denom_classes)

                    all_classes[r['time'] + "_"+ denom_key] = denom_classes

                results[indicator.id]['natural_breaks'] = all_classes

        except Indicator.DoesNotExist:
            continue

    return HttpResponse(json.dumps(results), mimetype="application/json")

def geojson(request):
    """ JSON access to geographies """
    records = GeoRecord.objects.filter(pk__in=map(lambda rid_str: int(rid_str), request.GET.getlist('record'))).geojson()
    result = '{"type": "FeatureCollection", "features": []}'

    features = []
    for record in records:
        properties = json.dumps({'label': record.name, 'key': record.geo_id,
            'level': {'name':record.level.name, 'slug':record.level.slug},'slug':record.slug,})
        # simplejson will escape the json string returned by GeoDjango, so we have
        # to build the json string manually
        features.append('{"type": "Feature", "properties": %s,"geometry": %s}' % (properties, record.geojson))

    result = '{"type": "FeatureCollection", "features": [%s]}' % ','.join(features)
    return HttpResponse(result, mimetype="application/json")



#---------------------------CSV EXPORT ------------------------------------------------------------------------

def export_csv(request):
    """ Export Indicators for given geo_records. Indicator ids are passed via GET as &i=, Geo Record id's are passed as '&r=' years can be limited with &time=
    ex:profiles/export/?r=46&r=61&r=121&i=141&i=93&i=92

    Sample csv output
    geography,indicator, time1, time2, time3, change
    """
    indicators_data = []
    times = request.GET.getlist('time')
    sorted_times = {}

    if 'r' in request.GET and request.GET.get('r') != None and request.GET.get('r') != '':
        if request.GET.get('r') != 'smt':
            geo_record_ids = request.GET.getlist('r')
        else:
            # we need to build our own geo_records
            geo_record_ids = None
    else:
        raise Http404('Bad Request')

    # check for indicator ids
    if 'i' in request.GET:
        if geo_record_ids:
            # clean up all the incoming data.
            indicator_ids = []
            geo_record_ids = []
            for i in request.GET.getlist('i'):
                try:
                    indicator_ids.append(int(i))
                except ValueError:
                    pass
            for g in request.GET.getlist('r'):
                try:
                    geo_record_ids.append(int(g))
                except ValueError:
                    pass
            for ind_id in indicator_ids:
                try:
                    ind = Indicator.objects.get(pk=ind_id, published=True)
                    #iterate geo records
                    for geo_id in geo_record_ids:
                        try:
                            record = GeoRecord.objects.get(pk=geo_id)
                            indicators_data.append(ind.get_indicator_info(record))
                        except GeoRecord.DoesNotExist:
                            continue
                except Indicator.DoesNotExist:
                    continue
        else:
            # we should only do one indicator.
            ind_id = request.GET.get('i')
            try:
                ind = Indicator.objects.get(pk=ind_id, published=True)
                st_level = GeoLevel.objects.get(slug='state')
                # start at the state
                state = GeoRecord.objects.get(level=st_level)
                indicators_data.append(ind.get_indicator_info(state))
                # now munis
                for m in state.child_records():
                    indicators_data.append(ind.get_indicator_info(m))
                    #now tracts
                    for t in m.child_records():
                        indicators_data.append(ind.get_indicator_info(t))
            except Indicator.DoesNotExist:
                 pass

        # sort times
        for ind in indicators_data:
            time_hash = "%s" % "&".join([t.name.replace(' ','') for t in ind['indicator_times']])
            if time_hash not in sorted_times:
                sorted_times[time_hash] = []
            sorted_times[time_hash].append(ind)

        zip_in_memory = StringIO.StringIO()
        zip_file_out = zipfile.ZipFile(zip_in_memory, "a", compression=zipfile.ZIP_DEFLATED)

        #write each time data to a different csv
        for time in sorted_times:
            csv_file = generate_export_csv(sorted_times[time])
            zip_file_out.writestr('%s.csv' %(time), csv_file.getvalue())
            csv_file.close()

        for file in zip_file_out.filelist:
            file.create_system = 0

        zip_file_out.close()

        response = HttpResponse(mimetype="application/zip")
        response["Content-Disposition"] = "attachment; filename=%s.zip" % "community_profiles_data"
        zip_in_memory.seek(0)
        response.write(zip_in_memory.read())

        return response

    raise Http404('Bad Request')


# BEGINS CSV EXPORT METHODS-------------------------------------------------------------------
def generate_export_csv(sorted_indicator_data):
    """ returns a csv file written to StringIO """
    csv_file = StringIO.StringIO()
    writer = csv.writer(csv_file)
    writer.writerow(get_indicator_csv_header(sorted_indicator_data[-1]))
    for indicator in sorted_indicator_data:
        writer.writerow(get_indicator_data_as_csv_row(indicator))
        for denom in indicator['denominators']:
            writer.writerow(get_denom_data_as_csv_row(denom, indicator['geo_record']))
    return csv_file

def get_indicator_csv_header(indicator_data):
    """ returns csv header row from indicator row """
    levels = get_default_levels()
    header = ()
    # build header out of geography... state, muni, tract
    header += levels
    header += ("indicator",)
    times = [(time.name, time.name + " MoE") for time in indicator_data['indicator_times']]
    header += tuple(t for time in times for t in time)
    header += ("change",)
    # distribution split up in times
    if indicator_data['indicator'].display_distribution:
        header += tuple(["distribution - " + time.name for time in indicator_data['indicator_times']])

    return header

def get_indicator_data_as_csv_row(indicator_data):
    levels = get_default_levels()
    row = ()
    row += tuple([indicator_data['geo_record'][lev_name] if lev_name in indicator_data['geo_record'] else ""\
                  for lev_name in levels])
    row += (indicator_data['indicator'].display_name,)
    values = [] # should be a list of tuples
    for key in indicator_data['values']:
        val = indicator_data['values'][key]
        val_tup = ()
        number = 0
        moe = 0
        percent = 0

        if val is not None:
            if val.moe != None:
                moe = float(val.moe)
            if val.number != None:
                number = float(val.number)
            val_tup += (number, moe,)
        values.append(val_tup)
    # flatten values
    row += tuple(v for val in values for v in val)
    row +=(float(indicator_data['change'].number) if indicator_data['change'] is not None else "",)
    if indicator_data['indicator'].display_distribution:
        try:
            if indicator_data['distribution'][key]:
                row +=tuple([float(indicator_data['distribution'][key].percent) if indicator_data['distribution'][key].percent != None  else 0 for key in indicator_data['distribution']])
            else:
                row +=tuple("")
        except AttributeError:
            row += tuple("")

    return row

def get_denom_data_as_csv_row(denominator, geo_record):
    levels = get_default_levels()
    row = ()
    row += tuple([geo_record[lev_name] if lev_name in geo_record else "" for lev_name in levels])
    row += (denominator['denominator'].label,)
    values = [(float(denominator['values'][key].percent),"") if denominator['values'][key]!= None else () for key in denominator['values']]
    row += tuple(v for val in values for v in val)
    row +=(float(denominator['change'].percent) if denominator['change']!=None else None,)

    return row
#-------------------------------------------------------------------------------------------


def search(request, template='search/search.html', load_all=True,
           form_class=ModelSearchForm, searchqueryset=None,
           context_class=RequestContext, extra_context=None, results_per_page=None):
    """
    A more traditional view that also demonstrate an alternative
    way to use Haystack.

    Useful as an example of for basing heavily custom views off of.

    Also has the benefit of thread-safety, which the ``SearchView`` class may
    not be.

    Template:: ``search/search.html``
    Context::
        * form
          An instance of the ``form_class``. (default: ``ModelSearchForm``)
        * page
          The current page of search results.
        * paginator
          A paginator instance for the results.
        * query
          The query received by the form.
    """
    query = ''
    data_domain_ids = []
    results = SearchQuerySet()

    geo_record, indicator = None, None
    try:
        geo_record = GeoRecord.objects.get(
            id=request.GET.get('gid', None))
    except (GeoRecord.DoesNotExist, ValueError):
        # the navigation template tag would pick DEFAULT_GEO_RECORD_ID if no
        # georecord is passed, but we should select it manually here so
        # thumbnails can be rendered in the proper context
        from maps.models import Setting
        setting = Setting.objects.filter(active=True);
        if len(setting) == 0:
           raise ImproperlyConfigured('DEFAULT_GEO_RECORD_ID must be defined')
        geo_record = GeoRecord.objects.get(id=setting[0].DEFAULT_GEO_RECORD_ID)

    indicator_results = None
    data_display_results = None

    def _value_to_display(indicator_result):
        datapoint = indicator_result.object.datapoint_set.filter(record=geo_record).order_by('-time__sort')
        value = None
        if datapoint:
            value = datapoint[0].value_set.all()
            if value:
                value = value[0]
        return (indicator_result, value)

    if request.GET.get('q') and request.GET.get('q') != None:
        data_domain_ids = map(lambda id: int(id), request.GET.getlist('data_domain'))
        query = request.GET.get('q')
        results = results.filter(content=query)
        indicator_results = results.filter(records=geo_record.id).models(Indicator)
        data_display_results = results.filter(record_id=geo_record.id).models(DataDisplay)

        if data_domain_ids:
            indicator_results = indicator_results.filter(domains__in=data_domain_ids)
            data_display_results = data_display_results.filter(domains__in=data_domain_ids)

        context = {
            'indicator_results': map(_value_to_display, indicator_results),
            'data_display_results': data_display_results,
            'total_results': data_display_results.count() + indicator_results.count(),
            'query': query,
            'geo_record': geo_record,
            'indicator': indicator,
            'data_domains': DataDomain.objects.all(),
            'data_domain_ids': data_domain_ids,
            'beta':settings.BETA
        }
    else:
        context = {}
    try:
        return render_to_response(template, context, context_instance=context_class(request))
    except AttributeError:
        context={'geo_record' : GeoRecord.objects.get(id=setting[0].DEFAULT_GEO_RECORD_ID)}
        return render_to_response(template, context, context_instance=context_class(request))
