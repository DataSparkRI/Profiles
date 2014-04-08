import urllib
import urllib2
from optparse import make_option

from django.conf import settings
from django.core.management.base import BaseCommand, CommandError
from django.utils import translation, simplejson as json
from django.db import transaction
from django.contrib.sites.models import Site
from django.core.files.base import ContentFile
from django.core.urlresolvers import reverse

from profiles.models import *

class Command(BaseCommand):
    option_list = BaseCommand.option_list + (
        make_option('--force-refresh', action='store_true', dest='force_refresh', default=False,
            help='Force a refresh of all images, even if they already exist'),
    )
    help = "Pre-renders images for various visualizations, mostly for thumbnails."
    args = "[--force-refresh]"
    
    def get_image(self, path):
        if not hasattr(settings, 'UNBROWSER_URL'):
            raise CommandError('Please specify the URL for an Unbrowser installation with the UNBROWSER_URL setting')
        
        post_data = {
            'url': 'http://' + Site.objects.get_current().domain + path,
            'format': 'png',
            'render_delay': 100
        }

        
        response = json.loads(urllib2.urlopen(
            settings.UNBROWSER_URL + '/webkit/rasterize/', 
            urllib.urlencode(post_data)
        ).read())
        if response['status'] == 'success':
            full_url = settings.UNBROWSER_URL + response['download_path']
            response = urllib2.urlopen(full_url)
            return response
        return None

    def handle(self, force_refresh=False, **options):
        displays = DataDisplay.objects.all()
        if not force_refresh:
            displays = displays.filter(image='')
        
        print "Generating Images for DataDisplay"
        for display in displays:
            img = self.get_image(display.get_absolute_url())
            if img:
                display.image.save(display.slug + '.png', ContentFile(img.read()))
        print "Done Generating Images for DataDisplay"
        
        data = DataPoint.objects.all()
        if not force_refresh:
            data = data.filter(image='')
        print "Generating Images for DataPoint"
        for i_data in data:
            img = self.get_image(reverse('indicator_display', kwargs={'indicatordata_id': i_data.id}))
            if img:
                i_data.image.save(str(i_data.id) + '.png', ContentFile(img.read()))
        print "Done generating Images for DataPoint"
