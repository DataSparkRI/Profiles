import locale
import re
import json
from StringIO import StringIO
from django.template.defaultfilters import slugify
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ValidationError
from huey.api import Huey
from huey.backends.base import BaseEventEmitter
from huey.backends.redis_backend import RedisBlockingQueue
from huey.backends.redis_backend import RedisDataStore
from huey.backends.redis_backend import RedisSchedule
from pyparsing import Word, Or, And, nums, alphas, alphanums, oneOf, ParseException

locale.setlocale(locale.LC_ALL, 'en_US.utf8')  # TODO: set locale based on request?

def get_levels_as_list(exclude=None):
    """ exclude: a list of levels to exclude """
    from profiles.models import GeoLevel
    from django.db.models import Q
    #  {id:1, name:"State", slug:"state", sumlev:"040"}
    levs_objs = GeoLevel.objects.filter(Q(year='') | Q(year=None))
    levs = []
    for l in levs_objs:
        if exclude!= None:
            if l.name != exclude.name:
                levs.append({'id':l.id, 'name':l.name, 'slug':l.slug, 'sumlev':l.summary_level})
            else:
                pass
        else:
            levs.append({'id':l.id, 'name':l.name, 'slug':l.slug, 'sumlev':l.summary_level})
    return sorted(levs, key=lambda k: k['sumlev'])

def get_indicator_levels_as_list(resource):
    from profiles.models import Indicator

    """ Return a sorted list of indicator levels"""
    if isinstance(resource, Indicator):
        levs_objs = resource.levels.all()
    else:
        #ints an
        levs_objs = resource.indicator.levels.all()

    levs = []
    for l in levs_objs:
        levs.append({'id':l.id, 'name':l.name, 'slug':l.slug, 'sumlev':l.summary_level})
    return sorted(levs, key=lambda k: k['sumlev'])

def get_default_levels():
    """ Return default levels defined in settings.
        Raise an error if they are not set.
    """
    from django.conf import settings
    levels = getattr(settings, 'DEFAULT_GEO_LEVELS', None)
    if levels is None:
        raise ValueError('DEFAULT_GEO_LEVELS must be defined in settings.py or local_settings.py')
    else:
        return levels

def format_number(num, data_type='COUNT', num_decimals=None, grouping=True):
    """ Provide consistent formatting for numbers.

    Defaults:
        count: show no decimals
        dollars: show no decimals, prefix with $
        percent: show one decimal, prefix with %

    Options:
        show_decimals: if not None, override the default behavior for
                        the selected data_type, and display this number of
                        decimals
    """
    if num is None:
        return ''

    if data_type == 'AVERAGE_OR_MEDIAN':
        data_type = 'PERCENT'  # This is a valid option in profiles.models.Indicator,
                               # but we can treat it as a percent here
    prefix = ''

    if data_type == 'DOLLARS' or data_type == 'AVERAGE_OR_MEDIAN_DOLLARS':
        prefix = '$'

        if num < 0:

            prefix = '-' + prefix
            num *= -1
    if data_type == 'DECIMAL_1' or data_type == 'DECIMAL':
        # Decimal Data type doesnt mean percent or $ it just needs to display decimals.
        num_decimals = 1

    if data_type == 'DECIMAL_2':
        # Decimal Data type doesnt mean percent or $ it just needs to display decimals.
        num_decimals = 2

    if num_decimals is None:
        if data_type == 'PERCENT':
            num_decimals = 1
        else:
            num_decimals = 0
    if data_type == 'YEAR':
        num_decimals = 0

    format_str = "%%s%%.%df" % num_decimals
    return locale.format_string(format_str, (prefix, num,), grouping=grouping)

def unique_slugify(instance, value, slug_field_name='slug', queryset=None,
                   slug_separator='-'):
    """
    Calculates and stores a unique slug of ``value`` for an instance.

    ``slug_field_name`` should be a string matching the name of the field to
    store the slug in (and the field to check against for uniqueness).

    ``queryset`` usually doesn't need to be explicitly provided - it'll default
    to using the ``.all()`` queryset from the model's default manager.
    """
    slug_field = instance._meta.get_field(slug_field_name)

    slug = getattr(instance, slug_field.attname)
    slug_len = slug_field.max_length

    # Sort out the initial slug, limiting its length if necessary.
    slug = slugify(value)
    if slug_len:
        slug = slug[:slug_len]
    slug = _slug_strip(slug, slug_separator)
    original_slug = slug

    # Create the queryset if one wasn't explicitly provided and exclude the
    # current instance from the queryset.
    if queryset is None:
        queryset = instance.__class__._default_manager.all()
    if instance.pk:
        queryset = queryset.exclude(pk=instance.pk)

    # Find a unique slug. If one matches, at '-2' to the end and try again
    # (then '-3', etc).
    next = 2
    while not slug or queryset.filter(**{slug_field_name: slug}):
        slug = original_slug
        end = '%s%s' % (slug_separator, next)
        if slug_len and len(slug) + len(end) > slug_len:
            slug = slug[:slug_len - len(end)]
            slug = _slug_strip(slug, slug_separator)
        slug = '%s%s' % (slug, end)
        next += 1

    setattr(instance, slug_field.attname, slug)

def _slug_strip(value, separator='-'):
    """
    Cleans up a slug by removing slug separator characters that occur at the
    beginning or end of a slug.

    If an alternate separator is used, it will also replace any instances of
    the default '-' separator with the new separator.
    """

    separator = separator or ''
    if separator == '-' or not separator:
        re_sep = '-'
    else:
        re_sep = '(?:-|%s)' % re.escape(separator)
    # Remove multiple instances and if an alternate separator is provided,
    # replace the default '-' separator.
    if separator != re_sep:
        value = re.sub('%s+' % re_sep, separator, value)
    # Remove separator from the beginning and end of the slug.
    if separator:
        if separator != '-':
            re_sep = re.escape(separator)
        value = re.sub(r'^%s+|%s+$' % (re_sep, re_sep), '', value)
    return value

def get_time_sorted_indicatorset(indicators, geo_record, data_domain):
    """
        Returns a dictionary of indicators grouped by Times
        TODO: Its strange that is here and it should be moved.
    """
    sorted_indicators = {}

    for indicator in indicators:
        # iterate through times
        time_key = ''
        times_list = [t.name for t in indicator.get_times()]
        times_list.sort(reverse=True)

        time_key = time_key.join(times_list)
        #indicator_info = get_indicator_info(indicator,times,geo_record,data_domain)
        indicator_info = indicator.get_indicator_info(geo_record, [], data_domain)

        # store the key in sorted_indicators if it doesnt exist and append the value
        if time_key not in sorted_indicators:
            sorted_indicators[time_key] = {'indicators':[], 'times':None,'display_change':False}

        sorted_indicators[time_key]['indicators'].append(indicator_info)
        sorted_indicators[time_key]['times'] = times_list

        #display_change
        display_change_flags=[]
        for s_i in sorted_indicators[time_key]['indicators']:
            display_change_flags.append(s_i['indicator'].display_change)

        sorted_indicators[time_key]['display_change'] = True in display_change_flags
    return sorted_indicators

def clear_memcache():
    try:
        import memcache
        mc = memcache.Client(['127.0.0.1:11211'], debug=0)
        mc.flush_all()
        return "Memcache cleared"
    except ImportError:
        return "Failed: python-memcache not installed"

def rebuild_search_index():
    from profiles.tasks import update_search_index
    task_data = update_search_index()
    return "Search Index Updated! TaskId: " + task_data.task.task_id

def generate_indicator_data(ind_id):
    from profiles.tasks import generate_indicator_data
    from profiles.models import Indicator, IndicatorTask, TaskStatus
    ind = Indicator.objects.get(pk=int(ind_id))
    async_obj = generate_indicator_data(ind)
    obj, created = TaskStatus.objects.get_or_create(status = "Pending", traceback="", error=False, t_id = str(async_obj.task.task_id))
    ind_task = IndicatorTask.objects.create(task_id = async_obj.task.task_id, indicator = ind)
    return "Generating Data for Indicator %s TaskId: %s" % (ind.display_name, async_obj.task.task_id)

def values_to_lists(value_list):
    """ Turn a list of Value Objects into 3 clean lists """
    numbers = []
    percents = []
    moes = []
    for v in value_list:
        if v.number:
            numbers.append(v.number)
        if v.percent:
            percents.append(v.percent)
        if v.moe:
            moes.append(v.moe)

    return numbers, percents, moes

def context_processor(request):
    from django.conf import settings
    beta = getattr(settings, 'BETA', False)
    skin = getattr(settings, 'CSS_SKIN', 'skin-ri.css')
    banner_text = getattr(settings, 'BANNER_TEXT', 'Community Profiles')
    api_url =  getattr(settings, 'PROFILES_API_URL', 'http://127.0.0.1:8080')
    app_host = request.META['HTTP_HOST'] #TODO: this may be incorrect
    sentry_js = getattr(settings, 'SENTRY_JS', '')
    center_map = getattr(settings, 'CENTER_MAP', '[0,0]')

    return {
        'BETA':beta,
        'CSS_SKIN': skin,
        'BANNER_TEXT': banner_text,
        'API_URL':api_url,
        'APP_HOST':app_host,
        'SENTRY_JS':sentry_js,
        'CENTER_MAP':center_map,
    }

############################################
# TASK QUEUE
#############################################

class ProfilesEventEmitter(BaseEventEmitter):
    def __init__(self, channel, **connection):
        super(ProfilesEventEmitter, self).__init__(channel, **connection)

    def emit(self, message):
        from profiles.models import TaskStatus
        message = json.loads(message)
        status = message.get('status', None)
        t_id = message.get('id', None)
        task_name= message.get('task', None)
        error = message.get('error', False)
        traceback = message.get('traceback', None)
        try:
            t = TaskStatus.objects.get(t_id = str(t_id))
            t.task = task_name
            t.status = status
            t.traceback = traceback
            t.error = error
            t.save()
        except TaskStatus.DoesNotExist:
            t = TaskStatus(status = status, traceback=traceback, error=error, task = task_name, t_id = str(t_id))
            t.save()



class ProfilesHuey(Huey):
     def __init__(self, name='profiles-huey', store_none=False, always_eager=False, **conn_kwargs):
        queue = RedisBlockingQueue(name, **conn_kwargs)
        result_store = RedisDataStore(name, **conn_kwargs)
        schedule = RedisSchedule(name, **conn_kwargs)
        events = ProfilesEventEmitter(name, **conn_kwargs)

        super(ProfilesHuey, self).__init__(
                queue=queue,
                result_store=result_store,
                schedule=schedule,
                events=events,
                store_none=store_none,
                always_eager=always_eager)


#########################
# Op parser #
#########################

def parse_value_comparison(op_string):
    """ Ex:
        10
        <=10
        <10
        >=10
        >10
    """
    num = Word(nums + ".") # matches 1 or 1.1
    ltgt = oneOf("< <= > >=")

    parser = num | And([ltgt, num])
    try:
        return parser.parseString(op_string).asList()
    except ParseException:
        #:TODO what should really happen here?
        raise ValueError("'%s' is not a Valid operation" % op_string)

def build_value_comparison(op_string):
    """ Returns a function based on a parsed op string string"""
    raw_op = parse_value_comparison(op_string)

    if len(raw_op) > 1:
        # this is a < > operation
        if raw_op[0] == "<":
            return lambda x: x < float(raw_op[1])
        if raw_op[0] == "<=":
            return lambda x: x <= float(raw_op[1])
        if raw_op[0] == ">":
            return lambda x: x > float(raw_op[1])
        if raw_op[0] == ">=":
            return lambda x: x >= float(raw_op[1])
    else:
        return lambda x: float(x) == float(raw_op[0])





