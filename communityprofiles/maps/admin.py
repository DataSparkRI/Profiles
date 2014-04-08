from django.contrib import admin
from maps.models import *
from maps.forms import *

class ShapeFileInline(admin.StackedInline):
    model = ShapeFile
    extra = 1

class MapLayerAdmin(admin.ModelAdmin):
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

class MapFeatureAdmin(admin.ModelAdmin):
    list_display = ('label', 'geo_key', 'source')

admin.site.register(ShapeFile, ShapeFileAdmin)
admin.site.register(PolygonMapFeature, MapFeatureAdmin)
admin.site.register(LineStringMapFeature, MapFeatureAdmin)
admin.site.register(PointMapFeature, MapFeatureAdmin)
admin.site.register(MapLayer, MapLayerAdmin)
