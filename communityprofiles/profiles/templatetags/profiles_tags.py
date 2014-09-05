from django import template
from django.core.urlresolvers import reverse
from django.conf import settings
from pylmth.dom import *
from profiles.models import (DataDomain, Time, GeoRecord, GeoLevel,
                                Value, DataPoint, Indicator, IndicatorPart)
from profiles.utils import format_number as util_format_number
from profiles.utils import get_time_sorted_indicatorset
from data_displays.models import DataDisplayTemplate, DataDisplay
from django.contrib.humanize.templatetags.humanize import intcomma
from django.utils.encoding import smart_str, force_unicode
from django.utils.safestring import mark_safe
from django.contrib.flatpages.models import FlatPage

import re
from maps.models import Setting
setting = Setting.objects.filter(active=True)
if len(setting) == 0:
   raise ImproperlyConfigured('DEFAULT_GEO_RECORD_ID must be defined')
setting = setting[0]

register = template.Library()

def ind_qfilter(qs, level):
    """Filter an indicator query set by a level"""
    return qs.filter(levels__in=[level])

register.filter('ind_qfilter', ind_qfilter)

def group_filter(group, level):
    from profiles.models import GroupIndex
    index = GroupIndex.objects.filter(groups = group)
    list = group.sorted_indicators(level)
    a = []
    for i in index:
        a.append(i.order)
    b = sorted(a)
    order = []
    for i in b:
        order.append(a.index(i))
    try:
       result = []
       for i in [list[i] for i in order]:
           if i.published == True:
              result.append(i)
       
       return result #[list[i] for i in order]
    except:
       return group.sorted_indicators(level)

register.filter('group_filter', group_filter)


def add_order_key(jstring, order_id):
    """ add an order: key to json string """
    jstring = jstring.replace('}',',"order_key":%s}' % order_id)
    return jstring

register.filter('order_key', add_order_key)

#TODO: Dont know why the built in flatpages templatetag was causing such a headache. This is hacky.
@register.simple_tag
def get_all_flatpages(current_fp_id=None):
    from django.contrib.flatpages.models import FlatPage
    fps = FlatPage.objects.all().order_by('title')
    l = '<ul class="flatpage_list">'
    for f in fps:
        if f.id != current_fp_id:
            l += '<li> <a href="%s">%s</a></li>' % (f.url, f.title)
        else:
            l += '<li class="active"> <a href="%s"> %s</a> </li>' % (f.url, f.title)

    l += "</ul>"
    return l

def _indicator_href(indicator, geo_record, data_domain=None):
    from django.contrib.flatpages.models import FlatPage
    # Get the href for the indicator, in the context of the selected geo_record and data_domain.
    # If no data_domain is passed, the default domain for that indicator is used
    if not data_domain:
        data_domain = indicator.default_domain()
    return reverse('indicator', kwargs={'geo_level_slug': geo_record.level.slug, 'geo_record_slug': geo_record.slug, 'data_domain_slug': data_domain.slug, 'indicator_slug': indicator.slug})


def _domain_href(domain, geo_record):
    # Get the href for the domain, in the context of the selected geo_record
    return reverse('data_domain', kwargs={'geo_level_slug': geo_record.level.slug, 'geo_record_slug': geo_record.slug, 'data_domain_slug': domain.slug})


@register.simple_tag(takes_context=True)
def record_href(context, record):
    data_domain = None
    data_domain_slug = None
    if context['data_domain']:
        data_domain = context['data_domain']
        data_domain_slug = data_domain.slug
    if context['indicator']:
        indicator = context['indicator']
        return _indicator_href(indicator, record, data_domain)
    else:
        return reverse('data_domain', kwargs={'geo_level_slug': record.level.slug, 'geo_record_slug': record.slug, 'data_domain_slug': data_domain_slug})


@register.inclusion_tag('profiles/includes/data_domains.html', takes_context=True)
def data_domains(context, geo_record=None, selected_domain=None):
    setting = Setting.objects.filter(active=True);
    if len(setting) == 0:
    #if geo_record == None:
        geo_record = GeoRecord.objects.get(pk=getattr(settings, "DEFAULT_GEO_RECORD_ID", 1))

    data_domains = [{'domain':domain,'href':_domain_href(domain, geo_record), }for domain in DataDomain.objects.filter(subdomain_only=False)]

    return {'data_domains': data_domains, 'selected_domain': selected_domain}


@register.inclusion_tag('profiles/includes/indicators.html')
def indicators(geo_level, geo_record, data_domain=None):
    indicators = [(indicator, _indicator_href(indicator, geo_record, data_domain)) for indicator in data_domain.indicators.all()]
    return {'indicators': indicators, }


@register.inclusion_tag('profiles/includes/datatables/attributes.html')
def attributes_table(indicator, geo_record, data_domain):
    times = Time.objects.filter(indicatorpart__indicator=indicator).order_by('sort').distinct()
    attributes = GeoRecord.objects.filter(parent=geo_record).order_by('name')
    if attributes.count() == 0:
        # if we're at the bottom of the geo hierarchy, display siblings
        attributes = GeoRecord.objects.filter(parent=geo_record.parent)
    attributes_and_href = [(attribute, _indicator_href(indicator, attribute, data_domain)) for attribute in attributes]

    return {'indicator': indicator, 'times': times, 'geo_record': geo_record, 'attributes': attributes_and_href}


#@register.inclusion_tag('profiles/includes/datatables/indicators.html')
@register.simple_tag
def indicators_table(title, indicators, geo_record, data_domain):
    """
    title: the name of the data domain
    indicators: A list of indicator objects
    get_record: the current GeoRecord
    data_domain: the current DataDomain
    """
    import markdown
    try:
        indicators = indicators.order_by('display_name')
    except AttributeError:
        # its a single indicator
        indicators = [indicators]

    sorted_indicators = get_time_sorted_indicatorset(indicators, geo_record, data_domain)
    tables = ''
    # build tables
    for i in sorted_indicators:
        ind_set = sorted_indicators[i]
        tbl = Table()
        tbl.attr.className = "table table-bordered data-table" + " times_%s" % len(ind_set['times'])
        thead = tbl.add_header()
        thr = thead.add_row()
        thcol = thr.add_col()
        thcol.add_attr('data-original-title')
        thcol.attr.data_original_title = 'Click an Indicator name to map'
        thcol.add_attr('rel')
        thcol.attr.rel="tooltip"
        thcol.attr.className="field_lbl indicator-lbl"
        thcol.inner_text='Indicator'
        #thr.add_col(className='field_lbl indicator-lbl', inner_text='Indicator')
        for t in ind_set['times']:
            thr.add_col(colspan='2', className='field_lbl', inner_text=t)
        if ind_set['display_change']:
            thr.add_col(colspan='1', inner_text='Change')
        #thr.add_col(colspan='1', inner_text='Notes', className='notes-col')

        #tbody
        tbody = tbl.add_body()
        for i_set in ind_set['indicators']:
            umoe=False # keeps track of unacceptable moe
            ind = i_set['indicator']
            i_vals = i_set['values']
            i_times = i_set['indicator_times'] # times objs
            i_times.sort(key=lambda tm: tm.name, reverse=True)
            suppressed_val = False
            tbr = tbody.add_row() #tr
            tbr.attr.id = ind.id
            ind_col = tbr.add_col(className='indicator-name') # this is the indicator title
            ind_col.add_attr('data-original-title')
            ind_col.attr.data_original_title = 'Click to map'
            ind_col.attr.rel = "tooltip"
            cell_wrap = Div()
            cell_wrap.attr.className="cell-wrap"
            cell_wrap.inner_html = '<a href="%s">%s</a>' % (i_set['href'], ind.display_name)
            ind_col.append_child(cell_wrap)
            #-----------------------------------------------------------------------------------notes
            notes = ind.get_notes()
            if notes:
                n_href = A()
                cell_wrap.append_child(n_href)
                n_href.add_attr('date-toggle')

                n_href.data_toggle = "modal"
                n_href.attr.className = "notes-icon"
                n_href.attr.href = "#%s_notes_modal" % ind.slug
                modal = Div()
                cell_wrap.append_child(modal)
                modal.attr.className = "modal hide"
                modal.attr.id = "%s_notes_modal" % ind.slug
                m_header = Div()
                m_header.attr.className = "modal-header"
                m_header.inner_html ="<h3>%s</h3>" % ind.display_name
                m_body = Div()
                m_body.attr.className = "modal-body"
                # append fields
                for n in notes:
                    m_body.inner_html += u'<h4>%s</h4>' % n['label']
                    m_body.inner_html += u'<p>%s</p>' % mark_safe(markdown.markdown(n['text']))

                modal.append_child(m_header, m_body)

            ###############################################Table values################################################33
            for t in i_times:
                # values are keyed to time by the time id
                raw_val = i_vals[t.id] # Value Object
                if raw_val: # check if there is a value
                    d_val = raw_val.to_dict()
                    f_val = d_val['f_number']
                    if f_val == "-1":
                        suppressed_val = True
                    td = tbr.add_col()
                    if raw_val.moe: # check to see if there is MOe, if so we need some fancy classes and attrs to display twitter bs(bootstrap that is) :D
                        td.add_attr('data-original-title') # this is a custom attribute
                        td.attr.rel = 'tooltip'
                        td.attr.className = 'value moe'
                        td.attr.data_original_title = "Margin of Error: %s" % util_format_number(raw_val.moe, ind.data_type)
                        td.inner_html = '<span class="moe-icon">+/-</span>%s<span class="pr-moe">+/-%s</span>' % (f_val, raw_val.moe)
                        td.attr.colspan='2'
                        #check if moe is acceptable
                        if raw_val.moe >  raw_val.number:

                            umoe=True
                            td.attr.className +=' u-moe' # unacceptable moe
                            td.attr.data_original_title = "+/-%s </br>The Margin of Error for this value is larger than the value making it unreliable. " % util_format_number(raw_val.moe, ind.data_type)
                            td.inner_html = '<span class="moe-icon"><span class="u-moe"></span> +/-</span>%s<span class="pr-moe">+/-%s</span><div class="cell-wrap"></div>' % (f_val, raw_val.moe)

                    else:
                        # no moe
                        td.attr.className='value'
                        td.attr.colspan='2'
                        td.inner_html = '<div class="cell-wrap">%s</div>' % f_val
                else:
                    td = tbr.add_col(className="value empty none")
                    td.attr.colspan='2'

                # we need to insert a blank value cell here
                #tbr.add_col(className="value empty")

            #change
            if ind_set['display_change']:
                change_val = i_set['change'] # Value Obj
                if change_val and suppressed_val == False:
                    #if change_val.number:
                    #    tbr.add_col(className='value change-num',inner_text=util_format_number(change_val.number, ind.data_type))
                    #else:
                    #    tbr.add_col(className='value empty no-change-num')
                    if change_val.percent:
                        col = tbr.add_col(className='value change-perc', inner_text="%s%%" % util_format_number(change_val.percent, "PERCENT"))
                        if umoe:
                            col.attr.className +=' u-moe'
                    else:
                        tbr.add_col(className='value empty no-change-perc')
                else:
                    tbr.add_col(className="value empty change-none")
                    #tbr.add_col(className="value empty change-none")

            #denominators
            if suppressed_val == False:
                for denom in i_set['denominators']:
                    den = denom['denominator'] # the denominator obj
                    den_vals = denom['values']
                    dtr = tbody.add_row(className='denom') # denom tr
                    dtr.add_col(className='denom', inner_html='<div class="cell-wrap"><a href="%s?denom=%s">...as %s</a></div>' % (i_set['href'], den.id, den.label)) # denom label
                    # get vals with time keys
                    for t in i_times:
                        den_val = den_vals[t.id]
                        if den_val: # check if None
                            if den_val.percent:
                                dtr.add_col(className="value denom denom-perc",inner_text="%s%%" % util_format_number(den_val.percent, "PERCENT") )
                            else:
                                dtr.add_col(className="value empty no-denom-perc")
                            if den_val.number:
                                dtr.add_col(className="value denom denom-divsor",inner_text="%s" % util_format_number(den_val.number,ind.data_type ))
                            else:
                                dtr_col(className="value empty no-denom-divisor")
                        else:
                            dtr.add_col(className="value empty denom-none")
                            dtr.add_col(className="value empty denom-none")
                    # denom_change
                    if ind_set['display_change']:
                        change_val = denom['change'] # Value Obj
                        if change_val: # check if None
                            #dtr.add_col(className='value denom-change-num',inner_text=util_format_number(change_val.number))
                            if change_val.percent:
                                dtr.add_col(className='value denom-change-perc', inner_text="%spts" % util_format_number(change_val.percent, "PERCENT"))
                            else:
                                dtr.add_col(className="value empty no-denom-perc")
                        else:
                            dtr.add_col(className="value empty change-none")

        tables += str(tbl)

    return tables

def atoi(text):
    return int(text) if text.isdigit() else text

def natural_keys(text):
    return [ atoi(c) for c in re.split('(\d+)', text.name) ]


@register.simple_tag
def indicator_table(indicator, geo_record):
    """ This is the table in the Indicator View. A similar table to indicators_table except for a single indicator """
    # we display all nested geographies so lets collect those first
    name = geo_record.name
    if geo_record.level.name !="Census Tract":
        geo_children = geo_record.child_records().exclude(name=name)
    else:
        geo_children = geo_record.parent.child_records().exclude(name=name)

    # make sure the geography we are interested in is the first one.
    geos = list(geo_children)
    geos.insert(0, geo_record)

    times = [t.name for t in indicator.get_times()]
    times.sort(reverse=True)
    tables = ''

    tbl = Table() # the main table
    tbl.attr.className = "data-table"
    # build the table head
    thead = tbl.add_header()
    thr = thead.add_row()
    thcol = thr.add_col()
    thcol.attr.className = 'field_lbl indicator-lbl'
    #thcol.inner_text = indicator.display_name
    thcol.inner_html = indicator.display_name+'''<a href="#" class="about-indicator-inTable"><img src="'''+settings.STATIC_URL+'''css/img/info.png"/>
                </a>
    '''
    for t in times:
        thr.add_col(colspan='1', className='field_lbl', inner_text=t)

    if indicator.display_change:
        thr.add_col(colspan='1', inner_text='Change')

    tbody = tbl.add_body()
    geos.sort(key=natural_keys)
    for g in geos:
        val = indicator.get_values_as_dict(g)
        ind = val['indicator']
        denoms = val['denominators']
        tbr = tbody.add_row() #tr
        geo_col = tbr.add_col(className='indicator-name')
        cell_wrap = Div()
        cell_wrap.attr.className="cell-wrap"
        cell_wrap.inner_html = g.name
        geo_col.append_child(cell_wrap)
        # get values
        umoe=None
        for t in times:
            val_col = tbr.add_col(className='value')
            val_wrap = Div()
            val_wrap.attr.className="cell-wrap"
            try:
                if ind[t]['moe']:
                    val_col.add_attr('data-original-title')
                    val_col.attr.rel ='tooltip'
                    val_col.attr.className += " moe"
                    val_col.attr.data_original_title = "Margin of Error: %s" % ind[t]['f_moe']
                    val_wrap.inner_html = '<span class="moe-icon">+/-</span>%s<span class="pr-moe">+/-%s</span>' % (ind[t]['f_number'],ind[t]['f_moe'])

                    # now we check for acceptible moe's
                    if ind[t]['moe'] > ind[t]['number']:
                        umoe = True
                        val_col.attr.className +=' u-moe'
                        val_col.attr.data_original_title = "+/-%s </br>The Margin of Error for this value is larger than the value making it unreliable. " % ind[t]['f_moe']

                else:
                    val_wrap.inner_html = ind[t]['f_number']

            except KeyError:
                # no values
                val_wrap.attr.className+=" none"
            val_col.append_child(val_wrap)

        # change
        if indicator.display_change:
            val_col = tbr.add_col(className='value change')
            val_wrap = Div()
            val_wrap.attr.className="cell-wrap"
            if umoe:
                val_col.attr.className += ' u-moe'
            try:
                val_wrap.inner_html = ind['change']['f_number']
            except KeyError:
                #no values
                val_wrap.attr.className +=" none"
                val_col.attr.className += " none"

            val_col.append_child(val_wrap)

        # denoms
        for d in denoms:
            d_row = tbody.add_row() # denom row
            d_row.attr.className = 'denom-row'
            d_col = d_row.add_col()# denom name
            d_wrap = Div()
            d_wrap.attr.className='cell-wrap'
            d_wrap.inner_html = "...as {0}".format(d)
            d_col.append_child(d_wrap)
            # get values
            for t in times:
                val_col = d_row.add_col(className='value')
                val_wrap = Div()
                val_wrap.attr.className="cell-wrap"
                try:
                    val_wrap.inner_html = denoms[d][t]['f_percent']
                except KeyError:
                    val_wrap.attr.className+=" none"
                val_col.append_child(val_wrap)
            #change
            if indicator.display_change:
                val_col = d_row.add_col(className='value change')
                val_wrap = Div()
                val_wrap.attr.className="cell-wrap"
                try:
                    val_wrap.inner_html = denoms[d]['change']['f_percent'].replace('%','pts')
                except KeyError:
                    val_wrap.attr.className+=" none"
                val_col.append_child(val_wrap)

    tables += str(tbl)
    return tables

@register.simple_tag
def indicator_number(indicator, geo_record, time=None):
    try:
        datapoint = DataPoint.objects.get(indicator=indicator, record=geo_record, time=time)
        value = datapoint.value_set.get(denominator__isnull=True)
        f_num = "%s" % util_format_number(value.number, data_type=indicator.data_type)
        #check for moe
        if value.moe:
            # we need to format the moe a ltitle differently
            div = Div()
            div.add_attr('data-original-title')
            div.attr.data_original_title = 'Margin of Error: %s' % util_format_number(value.moe, data_type=indicator.data_type)
            div.attr.className='value-cell'
            div.attr.rel='tooltip'
            div.inner_text = f_num
            icon = Span()
            icon.attr.className = 'moe-icon attr-tbl'
            icon.inner_text= '&plusmn;'
            div.append_child(icon)
            return str(div)
        else:
            return f_num
    except (DataPoint.DoesNotExist, Value.DoesNotExist):
        return ''


@register.simple_tag
def indicator_percent(indicator, geo_record, time=None):
    try:
        datapoint = DataPoint.objects.get(indicator=indicator, record=geo_record, time=time)
        value = datapoint.value_set.get(denominator__isnull=True)
        return "%s" % util_format_number(value.percent)
    except (DataPoint.DoesNotExist, Value.DoesNotExist):
        return ''


@register.simple_tag
def indicator_moe(indicator, geo_record, time):
    try:
        datapoint = DataPoint.objects.get(indicator=indicator, record=geo_record, time=time)
        value = datapoint.value_set.get(denominator__isnull=True)
        return util_format_number(value.moe, data_type=indicator.data_type)
    except (DataPoint.DoesNotExist, Value.DoesNotExist):
        return ''


@register.simple_tag
def geo_mapping(geo_record, geo_level):
    mapped = geo_record.mapped_to(geo_level)
    return ', '.join(map(lambda m: m.geo_id, mapped))


def _geo_nav_context(context):
    "Create a context object to render geo nav widgets"
    from profiles.utils import get_default_levels
    levels = get_default_levels()
    geo_record = None
    indicator = None
    data_domain = None

    if 'geo_record' in context:
        geo_record = context['geo_record']
    if 'indicator' in context:
        indicator = context['indicator']
    if 'data_domain' in context:
        data_domain = context['data_domain']

    if geo_record == None:
        #if not hasattr(settings, 'DEFAULT_GEO_RECORD_ID'):
        #    raise Exception('No geo_record was selected, and DEFAULT_GEO_RECORD_ID was not configured.')
        try:
            geo_record = GeoRecord.objects.get(pk=setting.DEFAULT_GEO_RECORD_ID)
        except GeoRecord.DoesNotExist:
            geo_record = GeoRecord.objects.filter(level=GeoLevel.objects.get(slug=levels[0].lower()))[0]


    # construct a list of geo levels to display in nav, with a list of records
    # and optionally a selected record
    #geo_levels = GeoLevel.objects.filter(slug__in=[lev.lower() for lev in levels])
    nav = {}
    parent_level = geo_record.level.parent
    while parent_level:
        nav[parent_level.sort_key] = {'name':parent_level.name, 'pk':parent_level.pk, 'slug':parent_level.slug}
        parent_level = parent_level.parent

    # at this point any level that is not in nav already, is a sub level
    sub_levels = GeoLevel.objects.exclude(name__in=nav.keys()).filter(name__in=levels)
    for lev in sub_levels:
        nav[lev.sort_key] = {'name':lev.name, 'pk':lev.pk, 'slug':lev.slug}

    sorted(nav, key=lambda key: nav[key])
    # now legs get all the geographoes
    for k, v in nav.iteritems():
        lev = nav[k]
        lev['geos'] = GeoRecord.objects.filter(level__pk=lev['pk']).only('slug', 'pk', 'name')

    try:
        default_geo = GeoRecord.objects.get(pk=setting.DEFAULT_GEO_RECORD_ID)
    except GeoRecord.DoesNotExist:
        default_geo = GeoRecord.objects.filter(level=GeoLevel.objects.get(slug=levels[0].lower()))[0]
    try:
        del nav[1] # we never show the topmost geography
    except Exception as e:
        pass



    return {
        #'levels': levels,     # a list of the geo levels, with selections, to display
        'levels':nav,
        'data_domain': data_domain,  # currently selected domain
        'indicator': indicator,      # currently selected indicator
        'geo_record': geo_record,    # currently selected record
		'default_georecord':default_geo
    }



@register.inclusion_tag('profiles/includes/geo_nav.inc.html', takes_context=True)
def geo_nav(context):
    return _geo_nav_context(context)


@register.inclusion_tag('profiles/includes/search_geo_nav.inc.html', takes_context=True)
def search_geo_nav(context):
    return _geo_nav_context(context)


@register.simple_tag
def format_number(number, data_type='COUNT'):
	num = util_format_number(number, data_type=data_type)
	return num

@register.simple_tag
def get_state_for_geo(record):
    state = record.get_state()
    if state:
        return state.slug
    else:
        return record.slug


@register.inclusion_tag('profiles/includes/data_displays.inc.html')
def data_displays(geo_record, data_domain, featured_only = True, indicator=None):
    # we can get only featured ones
    if featured_only:
        featured_templates = DataDisplayTemplate.objects.filter(featured=True, domains=data_domain)
    else:
        featured_templates = DataDisplayTemplate.objects.all()

    displays = []

    for ddt in featured_templates:
        local_featured_displays = DataDisplay.objects.filter(template=ddt, record=geo_record)
        if len(local_featured_displays) != 0:
            displays += local_featured_displays
        else:
            # use the parent geography
            displays += DataDisplay.objects.filter(template=ddt, record=geo_record.parent)

    times = []

    for disp in displays:
        if disp.time not in times:
            times.append(disp.time)
    if times:
        times.sort(key=lambda time: time.sort, reverse=True)
        default_time = times[0].id
    else:
        default_time = 2000

    return {'data_displays': displays, 'default_time':default_time, 'times':times}


def profiles_admin_submit_row(context):
    """
    Displays the row of buttons for delete and save.
    """
    # capture model type so we can display a generate indicator data
    try:
        model = context['original']
    except KeyError:
        model = None
    opts = context['opts']
    change = context['change']
    is_popup = context['is_popup']
    save_as = context['save_as']
    return {
        'onclick_attrib': (opts.get_ordered_objects() and change
                            and 'onclick="submitOrderForm();"' or ''),
        'show_delete_link': (not is_popup and context['has_delete_permission']
                              and (change or context['show_delete'])),
        'show_save_as_new': not is_popup and change and save_as,
        'show_save_and_add_another': context['has_add_permission'] and
                            not is_popup and (not save_as or context['add']),
        'show_save_and_continue': not is_popup and context['has_change_permission'],
        'is_popup': is_popup,
        'show_save': True,
        'is_indicator':type(model) is Indicator,
        'model': model
    }
profiles_admin_submit_row = register.inclusion_tag('admin/submit_line.html', takes_context=True)(profiles_admin_submit_row)

@register.simple_tag
def google_analytics():
    return settings.GOOGLE_ANALYTICS_UID

@register.simple_tag
def logo_icon():
    return settings.LOGO_ICON

@register.simple_tag
def style_css():
    try:    
       return settings.STYLE
    except AttributeError:
       return "css/profiles.css"

@register.assignment_tag
def search_domainId(domain_id):
    from profiles.models import DataDomainIndex
    return DataDomainIndex.objects.filter(dataDomain_id=domain_id)

@register.assignment_tag
def search_groupId(group_id):
    from profiles.models import GroupIndex
    return GroupIndex.objects.filter(groups_id=group_id)
