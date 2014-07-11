import os, zipfile, re
from django.db import models
from django.contrib.gis.db import models
from django.core.files.storage import FileSystemStorage
from django.conf import settings
from django.contrib.gis.utils import LayerMapping
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

shp_file_storage = FileSystemStorage(location=settings.SHAPE_FILE_STORAGE_PATH)

class MapFeature(models.Model):
    source = models.ForeignKey('ShapeFile')
    geo_level = models.IntegerField(blank=True, null=True) # this is mostly here for convienience it should really not be used here #TODO: make this a django foriegn key, i was just to lazy to work out the circular import thing
    label = models.CharField(max_length=255, blank=True)
    geo_key = models.CharField(max_length=255, blank=True, help_text="A identifier that links this back to a Geo Record via the geoid Field", db_index=True)
    geo_meta = models.CharField(max_length=255, blank=True, help_text="Additional information")
    description = models.TextField(blank=True)

    objects = models.GeoManager()

    def save(self, *args, **kwargs):
        super(MapFeature, self).save(*args, **kwargs)
        if self.geo_level is None:
            l = self.source.get_geo_lev_id()
            if l is not None:
                self.geo_level = l
                self.save()

    class Meta:
        abstract = True

    def __unicode__(self):
        return self.label


class PolygonMapFeature(MapFeature):
    geom = models.MultiPolygonField(srid=4326)

class LineStringMapFeature(MapFeature):
    geom = models.LineStringField(srid=4326)

class PointMapFeature(MapFeature):
    geom = models.PointField(srid=4326)


class ShapeFile(models.Model):
    """ Defines a shapefile and its associated layers."""
    name = models.CharField(max_length=255, blank=True)
    label_column = models.CharField(max_length=255, blank=False, null=False, help_text="The Shape file column that should be used as a label")
    geo_key_column = models.CharField(max_length=255, blank=False, null=False, help_text="The Shape file column that should be used as to link this to a Geo Record's Name")
    geo_meta_key_column = models.CharField(max_length=255, blank=True, null=True, help_text="Meta values such as the containing geography's geo_key. Ex: What Muni is this tract in?")
    geom_type = models.CharField(max_length=255, blank=True, choices=(('linestring','Line String'), ('point', 'Point'), ('polygon','Polygon')))
    shape_file = models.FileField(storage=shp_file_storage, upload_to='files', null=True, blank=True, help_text='A .zip file that contains .shp file and .shx file. NOTE: Avoid naming your files with "_#.zip". Example "myfile_1.zip" This is due to how Django handles file name collisions. "01_myFile.zip" is fine.')
    color = models.CharField(max_length=255, blank=True, help_text='A valid html Hex color such as #E01B6A')
    zoom_threshold = models.IntegerField(default=5, help_text='The zoom level at which this layer becomes available on the map. The higher the number the more zoomed in you have to be.')

    def save(self, *args, **kwargs):
        """ Import the file and create Map Layers out of it """
        current_shp_file = self.shape_file.name
        super(ShapeFile, self).save(*args, **kwargs)
        # has the shape_file_changed?
        if current_shp_file != self.shape_file.name:
            self.import_shape_file()

    def get_geo_lev_id(self):
        from profiles.models import GeoLevel
        try:
            g = GeoLevel.objects.get(shapefile=self)
            return g.id
        except GeoLevel.DoesNotExist:
            return None

    def import_shape_file(self):
        """ Unzip uploaded file and import shape files.
            .shp file and .shx file should be in the zip file
            TODO:  VALIDATE file imports and TESTS
        """

        shp_file_zip = os.path.abspath(os.path.join(self.shape_file.path))
        shp_file_name = self.unzip_file(shp_file_zip, settings.SHAPE_FILE_STORAGE_PATH+"/files") # unzip to the shapefile storage directory
        # the path to the actual .shp file wich should have been in the zip
        # file.
        if shp_file_name is not None:
            # Because Django automatically increments files instead of renameing
            # them, we should strip out _\d+. this will turn file_8.zip into
            # file.zip which is probably the intended file name.
            cleaned_file_name = re.sub(r'_\d+.zip', '.zip', self.shape_file.name)
            shp_file = os.path.abspath(os.path.join(settings.SHAPE_FILE_STORAGE_PATH, "files", shp_file_name))
            ds = DataSource(shp_file)
            layer = ds[0]

            # Clean up any old Features that are associate with this shapefile
            # & Create a new MapFeature Based on its geom_type

            if layer.geom_type == 'Point':
                PointMapFeature.objects.filter(source=self).delete()

                for feature in layer:
                    geom = GEOSGeometry(feature.geom.wkt)
                    map_feat = PointMapFeature(
                            source = self,
                            label = feature.get(self.label_column),
                            geo_key  = feature.get(self.geo_key_column),
                            geom = geom
                    )
                    if self.geo_meta_key_column:
                        map_feat.geo_meta = feature.get(self.geo_meta_key_column)
                    map_feat.save()

            elif layer.geom_type == 'LineString':
                LineStringMapFeature.objects.filter(source=self).delete()

                for feature in layer:
                    geom = GEOSGeometry(feature.geom.wkt)
                    map_feat = LineStringMapFeature(
                                source = self,
                                label = feature.get(self.label_column),
                                geo_key  = feature.get(self.geo_key_column),
                                geom = geom
                    )
                    if self.geo_meta_key_column:
                        map_feat.geo_meta = feature.get(self.geo_meta_key_column)
                    map_feat.save()

            elif layer.geom_type == 'Polygon':
                PolygonMapFeature.objects.filter(source=self).delete()
                for feature in layer:
                    if feature.geom.geom_type == 'Polygon':
                        geom = MultiPolygon(GEOSGeometry(feature.geom.wkt))
                    if feature.geom.geom_type == 'MultiPolygon':
                        geom = GEOSGeometry(feature.geom.wkt)

                    map_feat = PolygonMapFeature(
                                source = self,
                                label = feature.get(self.label_column),
                                geo_key  = feature.get(self.geo_key_column),
                                geom = geom
                    )

                    if self.geo_meta_key_column:
                        map_feat.geo_meta = feature.get(self.geo_meta_key_column)
                    map_feat.save()


            else:
                raise ValueError('Geometry Type: %s Is not supported. Only Point, LineString, Polygon are currently supported' % layer.geom_type)


            map_feat.save()


    def unzip_file(self, src_zip, destination):
        """ Unzip src_zip to destination
            Return the name of the shape file in the directory or None if one is not found
        """
        zf = zipfile.ZipFile(src_zip)
        shp_file_name = None
        for name in zf.namelist():
            if os.path.splitext(name)[1] == ".shp":
                shp_file_name = name
            outfile = open(os.path.join(destination, name), 'wb')
            outfile.write(zf.read(name))
            outfile.close()

        return shp_file_name

    def __unicode__(self):
        return self.name

class PointOverlayIcon(models.Model):
    name = models.CharField(max_length=255)
    image = models.ImageField(upload_to='point_icons')

    def __unicode__(self):
        return self.name

class PointOverlay(models.Model):
    name = models.CharField(max_length=255)
    shapefile =  models.ForeignKey(ShapeFile, limit_choices_to={'geom_type': 'point'})
    icon =  models.ForeignKey(PointOverlayIcon)
    available_on_maps = models.BooleanField(default=False)

    def __unicode__(self):
        return self.name

class GeoFile(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    year = models.CharField(max_length=100)
    file = models.FileField(upload_to='data_files',help_text=' NOTE: Avoid naming your files with "_#.zip". Example "myfile_1.zip" This is due to how Django handles file name collisions. "01_myFile.zip" is fine.')
    added = models.DateTimeField(auto_now_add=True)

    def __unicode__(self):
        return self.name

class Setting(models.Model):
    DEFAULT_GEO_RECORD_ID = models.CharField(max_length=100)
    active = models.BooleanField(default=False)

    def __unicode__(self):
        return self.DEFAULT_GEO_RECORD_ID

def get_layers_for_geo(record):
    """ returns list of layers and features for given record"""
    map_layers = []
    level = record.level
    for layer in MapLayer.objects.filter(available_on_maps=True):

        l = {'name':layer.name, 'shapefiles':[]}

        for sf in layer.shapefiles.all():
            #get all features for current geography
            if level.slug == 'state':
                polygon_qs = PolygonMapFeature.objects.all().values('id')
                linestr_qs = LineStringMapFeature.objects.all().values('id')
                point_qs = PointMapFeature.objects.all().values('id')

            elif level.slug == 'municipality':
                polygon_qs = PolygonMapFeature.objects.filter(geo_key=record.name).values('id')
                linestr_qs = LineStringMapFeature.objects.filter(geo_key=record.name).values('id')
                point_qs = PointMapFeature.objects.filter(geo_key=record.name).values('id')

            elif level.slug =='census-tract':
                polygon_qs = PolygonMapFeature.objects.filter(geo_key=record.parent.name).values('id')
                linestr_qs = LineStringMapFeature.objects.filter(geo_key=record.parent.name).values('id')
                point_qs = PointMapFeature.objects.filter(geo_key=record.parent.name).values('id')

            shapefile = {'name':sf.name, 'color':sf.color, 'type':sf.geom_type, 'zoom':sf.zoom_threshold, 'features':{}}

            # collect the result of our queries
            shapefile['features']['polygons'] = [str(f['id']) for f in polygon_qs]
            shapefile['features']['points'] = [str(f['id']) for f in point_qs]
            shapefile['features']['linestring'] = [str(f['id']) for f in linestr_qs]

            # also create a tastypie resource friendly uri string for each
            # resource
            if shapefile['features']['polygons']:
                shapefile['features']['polygons_uri'] = ';'.join(shapefile['features']['polygons'])
            if shapefile['features']['points']:
                shapefile['features']['points_uri'] = ';'.join(shapefile['features']['points'])
            if shapefile['features']['linestring']:
                shapefile['features']['linestring_uri'] = ';'.join(shapefile['features']['linestring'])


            # append this shapefileset to the list if this shape file has at
            # least one feature to display
            if shapefile['features']['polygons'] or shapefile['features']['linestring'] or shapefile['features']['points']:
                l['shapefiles'].append(shapefile)

        ## only return layers with at least 1 good shapefile
        if len(l['shapefiles']) > 0:
            map_layers.append(l)

    return map_layers


