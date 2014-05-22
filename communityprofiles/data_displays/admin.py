from django.contrib.gis import admin
from data_displays.models import *
from radmin import console

class DataDisplayTemplateAdmin(admin.ModelAdmin):
    list_display = ('title', 'subtitle', 'subsubtitle', 'description')
    filter_horizontal = ('indicators',)
    exclude = ('source',)

    def formfield_for_manytomany(self, db_field, request, **kwargs):
        levs = ["State", "Municipality", "Census Tract"]
        if db_field.name == "levels":
            kwargs["queryset"] = GeoLevel.objects.filter(name__in=levs)
        if db_field.name == "records":
            kwargs["queryset"] = GeoRecord.objects.filter(level__in=GeoLevel.objects.filter(data_sources__isnull=True))
        return super(DataDisplayTemplateAdmin, self).formfield_for_manytomany(db_field, request, **kwargs)



class DataVisualizationPartInline(admin.TabularInline):
	model=DataVisualizationPart


class DataVisualizationAdmin(admin.ModelAdmin):
	inlines=[DataVisualizationPartInline]

#admin.site.register(DataDisplayTemplate, DataDisplayTemplateAdmin)
#admin.site.register(DataVisualizationResource)
#admin.site.register(DataVisualization,DataVisualizationAdmin)

console.register_to_model(DataDisplayTemplate, 'Render Display', 'data_displays.utils.admin_generate_data_display', True)


