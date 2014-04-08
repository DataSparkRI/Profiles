from django.db import models
from profiles.models import GeoRecord,GeoLevel,DataDomain, Indicator, IndicatorPart, Time
from profiles.utils import unique_slugify
from sorl.thumbnail import ImageField
from django.db.models.signals import pre_save, post_save
from django.core.urlresolvers import reverse


class DataVisualizationResource(models.Model):
    title = models.CharField(max_length=255)
    source_file = models.FileField(upload_to="viz", blank=True)
    url = models.CharField(max_length=300, blank=True)

    def __unicode__(self):
        return self.title


class DataVisualization(models.Model):
    """Represents an avilable group of resources that make up a visualization to include in a template"""
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.title

    def get_css_resources(self):
        resources = DataVisualizationPart.objects.filter(visualization=self).order_by('load_order')
        css_resources=[]

        for item in resources:
            if item.resource.source_file:
                """there is an uploaded file specified"""
                if ".css" in item.resource.source_file.url:
                    css_resources.append(item.resource.source_file.url)
                elif item.resource.url != '':
                    """there is url specified"""
                    if ".css" in item.resource.url:
                        css_resources.append(item.resource.url)

        return css_resources

    def get_js_resources(self):
        resources = DataVisualizationPart.objects.filter(visualization=self).order_by('load_order')

        js_resources=[]
        for item in resources:

            if item.resource.source_file:
                """there is an uploaded file specified"""
                if ".js" in item.resource.source_file.url:
                    js_resources.append(item.resource.source_file.url)
            elif item.resource.url != '':
                """there is url specified"""
                if ".js" in item.resource.url:
                    js_resources.append(item.resource.url)
        return js_resources


class DataVisualizationPart(models.Model):
	visualization = models.ForeignKey('DataVisualization', blank=True)
	resource = models.ForeignKey('DataVisualizationResource', blank=True)
	load_order = models.IntegerField(default=0, blank=True)


class DataDisplayTemplate(models.Model):
    """Represents an available data visualization Example: Map, Map + ranking"""

    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True)
    subsubtitle = models.CharField(max_length=300, blank=True)
    description = models.TextField(blank=True)
    source = models.CharField(max_length=300, blank=True, default="U.S. Census Bureau")
    featured = models.BooleanField(default=False)
    visualizations = models.ManyToManyField(DataVisualization, blank=True)

    levels = models.ManyToManyField(GeoLevel, blank=True) # Levels limit where these displays are rendered and show up. If we where to select only State and Muni, we would not see Displays for Tracts
    domains = models.ManyToManyField(DataDomain, blank=True)
    #which indicator data to feed to this DataDisplay
    indicators = models.ManyToManyField(Indicator, blank=True)
    times = models.ManyToManyField(Time, blank=True)

    def __unicode__(self):
        return self.title

    def get_sources(self):
        """ Returns a filtered string comprized of source fields from indicators"""
        sources = []
        for ind in self.indicators.all():
            source = ind.source.strip()
            if source not in sources:
                sources.append(source)

        return ", ".join(sources)


    def render_display(self):
        """Create DataDisplays for each level of geography in the indicator

        """
        ## Delete existing DataDisplays
        DataDisplay.objects.filter(template=self).delete()

        #render only to specified levels
        levels = self.levels.all()
        slug_parts = [self.title]
        for level in levels:
            print "Rendering Level: %s" % level
            geo_records = GeoRecord.objects.filter(level=level)
            geo_records_count = len(geo_records)

            for geo_record in geo_records:
                ###Create a data_display for each geo record and time###
                for time in self.times.all():

                    data_display = DataDisplay(title=self.title,
						                       record=geo_record,
											   template=self,
											   time = time
												)
                    unique_slugify(data_display, ' '.join(slug_parts) + geo_record.slug+time.name ,queryset=DataDisplay.objects.all())
                    data_display.save()


class DataDisplay(models.Model):
    title = models.CharField(max_length=300)
    subtitle = models.CharField(max_length=300, blank=True)
    subsubtitle = models.CharField(max_length=300, blank=True)
    record = models.ForeignKey(GeoRecord, blank=True, null=True)
    time = models.ForeignKey(Time, blank=True, null=True)

    image = ImageField(upload_to='data_display_images', blank=True)
    template = models.ForeignKey(DataDisplayTemplate)
    html = models.TextField(blank=True)
    slug = models.SlugField(unique=True, max_length=300, blank=True)

    def get_absolute_url(self):
        return reverse('data_display', kwargs={'datadisplay_slug': self.slug})



