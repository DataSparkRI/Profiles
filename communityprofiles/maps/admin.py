from django.contrib.gis import admin
from maps.models import *
from maps.forms import *
from django.contrib import messages

class ShapeFileInline(admin.StackedInline):
    model = ShapeFile
    extra = 1

class PointOverlayIconAdmin(admin.ModelAdmin):
    inlines = [
    ]

class PointOverlayAdmin(admin.ModelAdmin):
    inlines = [
    ]

class PointMapFeatureInline(admin.TabularInline):
    model = PointMapFeature


class PolygonMapFeatureInline(admin.TabularInline):
    model = PolygonMapFeature


class LineStringMapFeatureInline(admin.TabularInline):
    model = LineStringMapFeature

class ShapeFileAdmin(admin.ModelAdmin):
    form = ShapeFileForm
    #inlines = [
    #        PointMapFeatureInline,
    #        PolygonMapFeatureInline,
    #        LineStringMapFeatureInline,
    #]

class MapFeatureAdmin(admin.OSMGeoAdmin):
    list_display = ('label', 'geo_key', 'source')

def gen_geo_level_and_record(modeladmin, request, queryset):
    from profiles.tasks import generate_geo_date
    from django.utils.safestring import mark_safe
    generate_geo_date(queryset)
    messages.add_message(request, messages.INFO,mark_safe("Add to task. 1. Use this <a href='/admin/profiles/geolevel/'>link</a> to setup your shape file. 2. Use this <a href='/admin/profiles/georecord/'>link</a> to find your defult id(first geo record). 3. Setup your default GEO Record ID <a href='/admin/maps/setting/'>here</a>."))


class GeoFileAdmin(admin.ModelAdmin):
    actions = [gen_geo_level_and_record]

admin.site.register(ShapeFile, ShapeFileAdmin)
admin.site.register(PolygonMapFeature, MapFeatureAdmin)
admin.site.register(LineStringMapFeature, MapFeatureAdmin)
admin.site.register(PointMapFeature, MapFeatureAdmin)
admin.site.register(PointOverlay, PointOverlayAdmin)
admin.site.register(PointOverlayIcon, PointOverlayIconAdmin)
admin.site.register(GeoFile, GeoFileAdmin)
admin.site.register(Setting)
