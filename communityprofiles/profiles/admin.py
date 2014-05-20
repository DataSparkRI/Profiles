from django.contrib.gis import admin
from profiles.models import *
from data_displays.models import DataDisplayTemplate
from radmin import console
from profiles.utils import get_default_levels
from django import forms
from django.db.models import Q
from adminsortable.admin import (SortableAdmin, SortableTabularInline, SortableStackedInline, SortableGenericStackedInline)
from django.http import HttpResponse
import csv
from django.utils.translation import ugettext_lazy as _
from django.contrib.admin import SimpleListFilter

class NextUpdateDateField(SimpleListFilter):
    title = _('next update data at')
    parameter_name = 'nextUpdate'
    def lookups(self, request, model_admin):

        return (
                ('past_date',_('Past date')),
                ('this_month',_('This month')),
                ('next_6',_('Next 6 months')),
                ('this_year',_('This year')),
        )
    def queryset(self, request, queryset):
        import datetime
        now = datetime.datetime.now()
        if self.value() == 'past_date':
            day = now + datetime.timedelta(-2)
            return queryset.filter(next_update_date__range=(day, now)).order_by('next_update_date')
        elif self.value() == 'this_month':
            return queryset.filter(next_update_date__year=now.year,
                                   next_update_date__month=now.month,).order_by('next_update_date')
        elif self.value() == 'next_6':
            day = now + datetime.timedelta(183)
            return queryset.filter(next_update_date__range=(now, day)).order_by('next_update_date')
        elif self.value() == 'this_year':
            return queryset.filter(next_update_date__year=now.year).order_by('next_update_date')
        else:
            return queryset

class TimeAdmin(admin.ModelAdmin):
    list_display = ('name', 'sort' )
admin.site.register(Time, TimeAdmin)

class DataDomainIndexInline(SortableTabularInline):
    model = DataDomainIndex
    #prepopulated_fields = {"name": ("group",)}
    fields = ('group',)


class GroupIndexInline(SortableTabularInline):
    model = GroupIndex
    fields = ('indicators',)


class GeoLevelAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    exclude = ('parent','data_sources')
    list_display = ('name', 'year' )

admin.site.register(GeoLevel, GeoLevelAdmin)


class GeoRecordAdmin(admin.OSMGeoAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'level', )
    list_filter = ('level', )
    #filter_horizontal = ['mappings', ]
    exclude = ('components','parent','mappings')

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field.name=='parent':
            querystring = request.path.split('/')[-2]
            obj = GeoRecord.objects.get(pk=int(querystring))
            lev_year = obj.level.year
            if lev_year == None:
                kwargs['queryset'] = GeoRecord.objects.filter(level__year__isnull=True)
            else:
                kwargs['queryset'] = GeoRecord.objects.filter(level__year=lev_year)

        return super(GeoRecordAdmin, self).formfield_for_foreignkey(db_field, request, **kwargs)

admin.site.register(GeoRecord, GeoRecordAdmin)

class DataSourceAdmin(admin.ModelAdmin):
    list_display = ('name', 'implementation', )


admin.site.register(DataSource, DataSourceAdmin)


class IndicatorPartInline(admin.TabularInline):
    model = IndicatorPart
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "levels":
            levs= get_default_levels()
            kwargs["queryset"] = GeoLevel.objects.filter(name__in=levs, year='')|GeoLevel.objects.exclude(name__in=levs).filter(year='')
        return super(IndicatorPartInline, self).formfield_for_manytomany(db_field, request, **kwargs)


class DenominatorPartInline(admin.TabularInline):
    model = DenominatorPart

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "levels":
            levs= get_default_levels()
            kwargs["queryset"] = GeoLevel.objects.filter(name__in=levs, year='')|GeoLevel.objects.exclude(name__in=levs).filter(year='')
        return super(DenominatorPartInline, self).formfield_for_manytomany(db_field, request, **kwargs)

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        # find the indicator being edited, so we can limit IndicatorPart selections
        indicator_id_querystring = request.path.split('/')[-2]

        indicator_id = -1
        if indicator_id_querystring != 'add':
            indicator_id = int(indicator_id_querystring)

        if db_field.name == "part":
            kwargs["queryset"] = IndicatorPart.objects.filter(indicator=indicator_id)
        if db_field.name == "denominator":
            kwargs["queryset"] = Denominator.objects.filter(indicator=indicator_id)
        return super(DenominatorPartInline, self).formfield_for_foreignkey(db_field, request, **kwargs)


class DenominatorInline(admin.TabularInline):
    model = Denominator


class IndicatorDomainInline(admin.TabularInline):
    model = IndicatorDomain
    extra = 1


class CustomValueInline(admin.TabularInline):
    model = CustomValue

class LegendOptionInline(admin.TabularInline):
    model = LegendOption
    extra = 0


class GroupAdmin(SortableAdmin):

    inlines = [GroupIndexInline,]
    list_filter = ("domain",)
    list_display = ("name",)
    search_fields = ['name']
    exclude = ('order',)
    ordering = ('name',)
admin.site.register(Group, GroupAdmin)


class DenominatorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("label",)}


admin.site.register(Denominator, DenominatorAdmin)


class IndicatorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_filter = (NextUpdateDateField,'published','data_type', 'indicatorpart__data_source', 'indicatorpart__time', 'data_domains__domain')
    list_display = ('name','published','display_name','levels_str', 'data_type', 'sources_str', 'times_str', 'domains_str', 'short_definition', 'last_generated_at')
    search_fields = ['display_name', 'name']
    # There seems to a bug in Django admin right now, which prevents making these fields editable
    #list_editable = ('short_definition', 'long_definition',)
    inlines = [
        IndicatorPartInline,
        DenominatorInline,
        DenominatorPartInline,
        IndicatorDomainInline,
        CustomValueInline,
        LegendOptionInline,
    ]

    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'slug', 'display_change','data_type','published', 'data_as_of',
                       'last_generated_at', 'last_modified_at', 'next_update_date')
        }),
        ('Extended Metadata', {

            'fields': ('short_definition', 'long_definition', 'purpose', 'universe', 'limitations', 'routine_use', 'notes','source' )
        }),
    )

    def levels_str(self, obj):
        return ', '.join(map(lambda l: l.name, obj.levels.all().order_by('name')))
    levels_str.short_description = 'Levels'

    def sources_str(self, obj):
        return ', '.join(map(lambda d: d.data_source.name, obj.indicatorpart_set.all().order_by('time__sort')))
    sources_str.short_description = 'Sources'

    def domains_str(self, obj):
        return ', '.join(map(lambda d: d.name, obj.data_domains.all().order_by('name')))
    domains_str.short_description = 'Data Domains'

    def times_str(self, obj):
        return ', '.join(map(lambda d: d.time.name, obj.indicatorpart_set.all().order_by('time__sort')))
    times_str.short_description = 'Time Periods'

admin.site.register(Indicator, IndicatorAdmin)


class IndicatorPartAdmin(admin.ModelAdmin):
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "levels":
            levs= get_default_levels()
            kwargs["queryset"] = GeoLevel.objects.filter(name__in=levs, year='')|GeoLevel.objects.exclude(name__in=levs).filter(year='')
        return super(IndicatorPartAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)

admin.site.register(IndicatorPart, IndicatorPartAdmin)


class DataDomainAdmin(SortableAdmin):
    inlines = [DataDomainIndexInline,]
    list_display = ('name','all_domains','all_subdomains', 'all_groups', 'subdomain_only', 'weight')
    list_editable = ('weight', )
    list_filter = ('subdomain_only',)
    ordering = ('name',)
    search_fields = ['name']
    exclude = ('order',)
    prepopulated_fields = {"slug": ("name",)}

    def all_domains(self, obj):
        return ",<br>\n".join([i.name for i in DataDomain.objects.filter(subdomains=obj)])
    all_domains.allow_tags = True
    def all_subdomains(self, obj):
        return ",<br>\n ".join([i.name for i in obj.subdomains.all()])
    all_subdomains.allow_tags = True
    def all_groups(self,obj):
        return ",<br>\n ".join([i.name for i in obj.group.all()])
    all_groups.allow_tags = True
admin.site.register(DataDomain, DataDomainAdmin)


class IndicatorDomainAdmin(admin.ModelAdmin):

    list_display = ('indicator', 'domain', 'default', )
    list_filter = ('indicator', 'domain', 'default', )

    def formfield_for_foreignkey(self, db_field, request, **kwargs):
        if db_field == "domain":
            kwargs["queryset"] = DataDomain
        return super(IndicatorDomainAdmin, self).formfield_for_foreignkey(db_field,request,**kwargs)

#admin.site.register(IndicatorDomain, IndicatorDomainAdmin)

class PrecalculatedValueAdmin(admin.ModelAdmin):
	def formfield_for_foreignkey(self, db_field, request, **kwargs):
		if db_field.name == "geo_record":
			levels = get_default_levels()
			kwargs["queryset"] = GeoRecord.objects.filter(level__in=levels).order_by('name')
		return super(PrecalculatedValueAdmin, self).formfield_for_foreignkey(db_field,request,**kwargs)

admin.site.register(PrecalculatedValue, PrecalculatedValueAdmin)

class ValueInline(admin.TabularInline):
    model=Value
    extra=1

class DataPointAdmin(admin.ModelAdmin):
    inlines = [
        ValueInline
    ]

class FlatValueAdmin(admin.ModelAdmin):
    search_fields = ['display_title', 'geography__name']
    list_display = ('display_title', 'geography_name','geography_geo_key', 'time_key', 'f_number', 'f_percent')


admin.site.register(DataPoint, DataPointAdmin)

class TaskStatusAdmin(admin.ModelAdmin):
    pass

admin.site.register(TaskStatus, TaskStatusAdmin)
#admin.site.register(IndicatorTask,)
admin.site.register(FlatValue, FlatValueAdmin)

admin.site.register(DataFile)

#--------radmin console------------
console.register_to_all('Clear Memcache', 'profiles.utils.clear_memcache', True)
console.register_to_all('Update Search Index', 'profiles.utils.rebuild_search_index', True)
console.register_to_model(Indicator, 'Generate Indicator Data', 'profiles.utils.generate_indicator_data', True)


#------------- ACTIONS -----------------#
def export_indicator_info(modeladmin, request, queryset):
    """ Export indicator info """
    response = HttpResponse(content_type="application/csv")
    response['Content-Disposition'] = 'attachment; filename="indicators.csv"'
    writer = csv.writer(response)
    writer.writerow(['Indicator', 'Part Formulas', 'Denom Formulas', 'Data Sources'])

    for q in queryset:
        ifs = ""
        dfs = ""
        for ip in q.indicatorpart_set.all():
            ifs += "{time}: {formula}|".format(time=ip.time.name, formula=ip.formula)
        for dp in q.denominatorpart_set.all():
            dfs += "{time}: {formula}|".format(time=dp.part.time.name, formula =dp.formula)
        writer.writerow([q.display_name, ifs, dfs, "|".join(q.get_source_names())])

    return response

admin.site.add_action(export_indicator_info, "Export Indicators Meta data")
