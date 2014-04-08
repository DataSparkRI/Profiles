from django import forms
from maps.models import ShapeFile
from django.core.exceptions import ValidationError
from django.db.models.fields.files import FieldFile
from maps.utils import *
from django.contrib.gis.gdal import DataSource
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

class ShapeFileForm(forms.ModelForm):
    class Meta:
        model = ShapeFile

    def clean_label_column(self):
        if self.cleaned_data['label_column'] == None:
            raise ValidationError('Label Column is required')
        return self.cleaned_data['label_column']

    def clean_geo_key_column (self):
        if self.cleaned_data['geo_key_column'] == None:
            raise ValidationError('Geo Key is required')
        return self.cleaned_data['geo_key_column']

    def clean_shape_file(self):

        if 'label_column' not in self.cleaned_data or 'geo_key_column' not in self.cleaned_data:
            raise ValidationError('Label Column and Geo Key column is required')

        file = self.cleaned_data['shape_file']
        if file is None:
            raise ValidationError('Please Choose a .zip file')

        if file != False:
            targ_dir = "/tmp/profiles_sf_tmp"
            if isinstance(file, FieldFile):
                file = os.path.abspath(os.path.join(file.path))
            # make targ_dir if it doesnt exist
            if not os.path.exists(targ_dir):
                os.makedirs(targ_dir)
            shp_file_name = unzip_file(file, targ_dir)
            if shp_file_name is not None:
                shp_file = os.path.abspath(os.path.join(targ_dir, shp_file_name))
                ds = DataSource(shp_file)
                layer = ds[0]
                # all we have to do here is validate the contents of the shapefile

                projection = layer.srs.name.lower() # example GCS_North_American_1983, GCS_WGS_1984 TODO: there should be a better way to check this
                #IDEALLY EPSG:4326

                if 'mercator' in projection or 'mercator' not in projection: # ALWAYS TRUE #TODO: need a way to validate shapefile projections
                    # Now check that Label Column is in the layer
                    if self.cleaned_data['label_column'] not in layer.fields:
                        raise ValidationError('Invalid Label Column. Fields are %s' % ', '.join(layer.fields))
                    # check if Geo Key Column is valid
                    print self.cleaned_data
                    if self.cleaned_data['geo_key_column'] not in layer.fields:
                        raise ValidationError('Invalid Geo Key Column. Fields are %s' % ', '.join(layer.fields))

                    return file
                else:
                    raise ValidationError('Invalid Shapefile. Please Use Mercator Projection, preferably EPSG:4326')
            else:
                raise ValidationError('Invalid Shapefile')
            #else:
            #    # it is a FieldFile which means they are just resaving
            #    return file
