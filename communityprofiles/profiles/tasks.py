from django.conf import settings
from django.core.management import call_command
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.files import File
#from celery.decorators import task
#from celery.task import task
#from celery.task.sets import subtaskeeeee
from data_displays.models import DataDisplay
from django.conf import settings
from subprocess import Popen, PIPE, STDOUT
import string
import random
from huey.djhuey import crontab, periodic_task, task
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

@task()
def generate_indicator_data(indicator):
    logger.debug("Generating indicator data for %s" % indicator.name)
    indicator.generate_data()
    #if indicator.display_percent==True:
    #    generate_indicator_distribution(indicator)
    if indicator.display_change==True:
        #generate_indicator_change(indicator)
        indicator.generate_change()

    #finally generate some flat tables
    generate_flat_values(indicator)
    return "Generating indicator data for %s" % indicator.name

@task()
def generate_indicator_distribution(indicator):
    indicator.generate_distribution()
    return "Generating distribution for %s..." % indicator


@task()
def generate_indicator_change(indicator):
    indicator.generate_change()

    return "Generating change for %s..." % indicator

@task()
def generate_flat_values_task(indicator):
    # No longer used
    logger.debug("Generating flatvalues data for %s" % indicator.name)
    generate_flat_values(indicator)
    return "Generating Flat Values for %s..." % indicator


def generate_flat_values(indicator):

    logger.debug("Generating flatvalues data for %s" % indicator.name)
    from profiles.models import GeoLevel, GeoRecord, Indicator, FlatValue
    from maps.models import ShapeFile, PolygonMapFeature
    from django.conf import settings
    from django.template.defaultfilters import slugify

    v_levels = getattr(settings, 'DEFAULT_GEO_LEVELS')
    #levels = GeoLevel.objects.filter(name__in=v_levels)
    #recs = GeoRecord.objects.filter(level__in=levels)
    levels = indicator.levels.all()
    recs = GeoRecord.objects.filter(level__in=levels)

    # Delete all previously generate records
    FlatValue.objects.filter(indicator=indicator).delete()

    for rec in recs:
        data = indicator.get_values_as_dict(rec)
        try:
            geom = rec.get_geom_id()
        except Exception as e:
            print e
            geom = None

        for time_key in data['indicator'].iterkeys():
            fv = FlatValue(
                indicator = indicator,
                indicator_slug = indicator.slug,
                display_title = indicator.display_name,
                geography = rec,
                geography_name = rec.name,
                geography_geo_key = rec.geo_id,
                geometry_id = geom,
                value_type = 'i',
                time_key = time_key, # this could be 'change'
                number = data['indicator'][time_key].get('number', None),
                moe = data['indicator'][time_key].get('moe', None),
                percent = data['indicator'][time_key].get('percent', None),
                f_number = data['indicator'][time_key].get('f_number', None),
                f_moe = data['indicator'][time_key].get('f_moe', None),
                f_percent = data['indicator'][time_key].get('f_percent', None),

            )
            fv.save()

        for denom_name in data['denominators'].iterkeys():
            for time_key in data['denominators'][denom_name].iterkeys():
                fv = FlatValue(
                    indicator = indicator,
                    indicator_slug = denom_name,
                    display_title = "%s - %s" % (indicator.display_name, data['denominators'][denom_name][time_key].get('label', '')),
                    geography = rec,
                    geography_name = rec.name,
                    geography_geo_key = rec.geo_id,
                    geometry_id = geom,
                    value_type = 'd',
                    time_key = time_key, # this could be change
                    number = data['denominators'][denom_name][time_key].get('number', None),
                    moe = data['denominators'][denom_name][time_key].get('moe', None),
                    percent = data['denominators'][denom_name][time_key].get('percent', None),
                    f_number = data['denominators'][denom_name][time_key].get('f_number', None),
                    f_moe = data['denominators'][denom_name][time_key].get('f_moe', None),
                    f_percent = data['denominators'][denom_name][time_key].get('f_percent', None),
                    numerator = data['indicator'][time_key].get('number', None),
                    numerator_moe = data['indicator'][time_key].get('moe', None),
                    f_numerator = data['indicator'][time_key].get('f_number', None),
                    f_numerator_moe = data['indicator'][time_key].get('f_moe', None),

                )
                fv.save()


@task()
def generate_data_display(display_template):
	# delete all displays that curretly exist based off this template
	DataDisplay.objects.filter(template = display_template).delete()
	display_template.render_display()
	subtask(generate_data_display_image(display_template))
	return "Generating Data Display Templates for %s" % display_template.title

def get_image(path):
    targ_url =  "http://" + Site.objects.get_current().domain + path
    rand =  ''.join(random.choice(string.ascii_uppercase + string.digits) for x in range(25))
    cmd = "phantomjs %s %s %s" % (settings.PHANTOM_JS_RENDERER,targ_url, settings.PHANTOM_JS_RENDER_DIR + rand + ".png")
    print "Rendering " + targ_url
    p = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
    output =  p.stdout.read()
    return File(open("/tmp/phantom/" + rand + ".png"))


@task()
def generate_data_display_image(data_display_template):

    displays = DataDisplay.objects.filter(template=data_display_template)
    for display in displays:
        img = get_image(display.get_absolute_url())
        if img:
            display.image.save(display.slug + '.png', ContentFile(img.read()))

@task()
def update_search_index():
    call_command('rebuild_index',interactive=False)

@task()
def generate_geo_date(geo_file):
    for geo in geo_file:
        call_command('load_geographies', settings.MEDIA_ROOT+"/"+str(geo.file), str(geo.year), verbosity=0)

