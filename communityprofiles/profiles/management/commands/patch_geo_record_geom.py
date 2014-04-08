from django.core.management.base import BaseCommand, CommandError
from maps.models import ShapeFile
from profiles.models import GeoRecord, GeoLevel

class Command(BaseCommand):
    args = '<shape_file_id>'

    def handle(self, *args, **options):
        tract_shape_file_id = args[0]
        muni_shape_file_id = args[1]

        tract_sf = ShapeFile.objects.get(pk=int(tract_shape_file_id))
        tracts = GeoRecord.objects.filter(level=GeoLevel.objects.get(name ='Census Tract'))
        for tract in tracts:
            tract.shapefile = tract_sf
            tract.save()

        muni_sf = ShapeFile.objects.get(pk=int(muni_shape_file_id))
        munis = GeoRecord.objects.filter(level=GeoLevel.objects.get(name ='Municipality'))
        for muni in munis:
            muni.shapefile = muni_sf
            muni.save()


