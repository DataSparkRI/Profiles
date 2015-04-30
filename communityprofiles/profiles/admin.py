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
from django.contrib import messages
from profiles.tasks import generate_indicator_data as generate_indicator_data_task
from time import sleep

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

def delete_all_lower_level_geo_record(modeladmin, request, queryset):
    from profiles.models import GeoRecord
    count = 0
    for obj in queryset:
        search = obj.geo_id_segments
        all = GeoRecord.objects.filter(geo_id_segments__icontains=search[:-1])
        count = count + all.count()
        all.delete()
    
    messages.add_message(request, messages.INFO, "%d geo records was removed."%count)

def rename_FlatValue(name,geography_id):
        from profiles.models import FlatValue
        objs = FlatValue.objects.filter(geography_id=geography_id)
        if len(objs) >0:
           if objs[0].geography_name != name:
              objs.update(geography_name = name)


def rename_with_upper_level(modeladmin, request, queryset):

    from profiles.models import GeoRecord
    count = 0
    for obj in queryset:
        tt = obj.geo_id_segments[:obj.geo_id_segments.rfind(",")]+"}"
        a = GeoRecord.objects.filter(geo_id_segments__icontains=tt)

        if len(a) > 0:           #have upper level
           upper_name = GeoRecord.objects.filter(geo_id_segments__icontains=tt)[0].name
           name = upper_name +" - "+obj.name
           rename_FlatValue(name,obj.id)
           obj.name = name
           obj.save()
           count = count + 1
    messages.add_message(request, messages.INFO, "%d geo records was updated."%count)

def rename_back_only_current_level(modeladmin, request, queryset):
    from profiles.models import GeoRecord
    count = 0
    for obj in queryset:
           name = obj.name.split("- ")[-1]
           rename_FlatValue(name,obj.id)
           obj.name = name
           obj.save()
           count = count + 1
    messages.add_message(request, messages.INFO, "%d geo records was updated."%count)


#---------------------------------------#

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

class LastGeneratedDateField(SimpleListFilter):
    title = _('last generated data at')
    parameter_name = 'lastGenerated'
    def lookups(self, request, model_admin):

        return (
                ('not_null',_('Not null/none')),
                ('null',_('Null/none')),
                ('last_day',_('Last day')),
                ('last_7_days',_('Last 7 days')),
                ('last_30_days',_('Last 30 days')),
        )
    def queryset(self, request, queryset):
        import datetime
        now = datetime.datetime.now()
        if self.value() == 'not_null':
            return queryset.filter(last_generated_at__isnull=False)
        elif self.value() == 'null':
            return queryset.filter(last_generated_at__isnull=True)
        elif self.value() == 'last_day':
            day = now + datetime.timedelta(-2)
            return queryset.filter(last_generated_at__range=(day, now)).order_by('last_generated_at')
        elif self.value() == 'last_7_days':
            day = now + datetime.timedelta(-8)
            return queryset.filter(last_generated_at__range=(day, now)).order_by('last_generated_at')
        elif self.value() == 'last_30_days':
            day = now + datetime.timedelta(-31)
            return queryset.filter(last_generated_at__range=(day, now)).order_by('last_generated_at')
        else:
            return queryset


class FinishedField(SimpleListFilter):
    title = _('Task statuses')
    parameter_name = 'statuses'
    def lookups(self, request, model_admin):

        return (
                ('not_finished',_('Not Finished')),
                ('finished',_('Finished')),
        )
    def queryset(self, request, queryset):
        from django.db.models import Q
        if self.value() == 'not_finished':
            return queryset.filter(~Q(status="finished"))
        elif self.value() == 'finished':
            return queryset.filter(status="finished")
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
    ordering = ('order',)

def generate_geo_record(modeladmin, request, queryset):
    from profiles.tasks import generate_geo_record_task
    from django.utils.safestring import mark_safe
    generate_geo_record_task(queryset)
    messages.add_message(request, messages.INFO,mark_safe("Add to task. It will create geo record based on your shape file."))

class GeoLevelAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
    exclude = ('parent','data_sources')
    list_display = ('name', 'year' )
    actions = [generate_geo_record]

admin.site.register(GeoLevel, GeoLevelAdmin)


class GeoRecordAdmin(admin.OSMGeoAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_display = ('name', 'level', )
    list_filter = ('level', )
    search_fields = ['name','notes']
    #filter_horizontal = ['mappings', ]
    exclude = ('components','parent','mappings')
    actions = [delete_all_lower_level_geo_record, rename_back_only_current_level, rename_with_upper_level]
    
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

class FormulaAdminFormset(forms.models.BaseInlineFormSet):
    def clean(self):
        for form in self.forms:
            str1 = str(form["formula"]).splitlines()
            if len(str1) > 2 or len(str1[1])>11: # have data
               if any("" == s for s in str1):
                  raise forms.ValidationError('Please remove extra Empty line in the formula.')
               if str1[-1][0]=='<':
                  raise forms.ValidationError('Please remove extra Enter on end of formula.')
               elif str1[1][0]==' ':
                  raise forms.ValidationError('Please remove extra Space on start of formula')
               elif str1[-1][-12]==' ':
                  raise forms.ValidationError('Please remove extra Space on end of formula')
               else:
                  pass

class IndicatorPartInline(SortableTabularInline):
    model = IndicatorPart
    formset= FormulaAdminFormset
    def formfield_for_manytomany(self, db_field, request, **kwargs):
        if db_field.name == "levels":
            levs= get_default_levels()
            kwargs["queryset"] = GeoLevel.objects.filter(name__in=levs, year='')|GeoLevel.objects.exclude(name__in=levs).filter(year='')
        return super(IndicatorPartInline, self).formfield_for_manytomany(db_field, request, **kwargs)


class DenominatorPartInline(SortableTabularInline):
    model = DenominatorPart
    formset= FormulaAdminFormset
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
    list_display = ("name","domains")
    search_fields = ['name']
    exclude = ('order',)
    ordering = ('name',)
    
    def domains(self, obj):
        return ", ".join([d.name for d in obj.domain.all()])
admin.site.register(Group, GroupAdmin)


class DenominatorAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("label",)}


admin.site.register(Denominator, DenominatorAdmin)

def generate_indicator_data(modeladmin, request, queryset):

    names = []
    for indicator in queryset:

        huey_task = generate_indicator_data_task(indicator)

        huey_task_id = huey_task.task.task_id

        indicator_task = IndicatorTask.objects.create(task_id=huey_task_id, indicator=indicator)

        sleep(1) #stagger the check to see if TaskStatus exists (task has started)

        if not TaskStatus.objects.filter(t_id = str(huey_task_id)).exists():
            TaskStatus.objects.create(status="pending", traceback="", error=False, t_id = str(huey_task_id))

        names.append(indicator.name)

    messages.add_message(request, messages.INFO, "Generating %s." % ', '.join(names))

class IndicatorAdmin(SortableAdmin):
    prepopulated_fields = {"slug": ("name",)}
    list_filter = (LastGeneratedDateField, NextUpdateDateField,'published','data_type', 'indicatorpart__data_source', 'indicatorpart__time', 'data_domains__domain')
    list_display = ('name','published','display_name','levels_str', 'data_type', 'sources_str', 'times_str', 'domains_str', 'universe', 'last_generated_at','last_modified_at')
    search_fields = ['display_name', 'name', 'id', 'short_definition']
    # There seems to a bug in Django admin right now, which prevents making these fields editable
    #list_editable = ('short_definition', 'long_definition',)
    inlines = [
        IndicatorPartInline,
        DenominatorInline,
        DenominatorPartInline,
        #IndicatorDomainInline,
        CustomValueInline,
        LegendOptionInline,
    ]
    actions = [generate_indicator_data, export_indicator_info]
    fieldsets = (
        (None, {
            'fields': ('name', 'display_name', 'slug', 'display_change','data_type','published', 'data_as_of',
                       'last_generated_at', 'last_modified_at', 'next_update_date')
        }),
        ('Extended netadaty', {

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
    domains_str.short_description = 'Groups'

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


#admin.site.register(DataPoint, DataPointAdmin)

class TaskStatusAdmin(admin.ModelAdmin):
    search_fields = ['unicode_name']
    list_display = ('__unicode__','last_updated')
    list_filter = ('status',FinishedField)

admin.site.register(TaskStatus, TaskStatusAdmin)
#admin.site.register(IndicatorTask,)
admin.site.register(FlatValue, FlatValueAdmin)

class DataFileAdmin(admin.ModelAdmin):
    search_fields = ['name', 'description']
    list_display= ('name',)

admin.site.register(DataFile, DataFileAdmin)

admin.site.register(Setting)

#--------radmin console------------
console.register_to_all('Clear Memcache', 'profiles.utils.clear_memcache', True)
console.register_to_all('Update Search Index', 'profiles.utils.rebuild_search_index', True)



