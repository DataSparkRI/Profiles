""" THIS MODULE IS DEPRECATED """
from django.utils import simplejson as json

from profiles.models import GeoRecord, GeoLevel, Time, Value
from maps import google
from choropleth import classes_and_colors
from profiles.utils import format_number
from django.contrib.gis.geos import Point

class CommProfilesMap(google.GoogleMap):
    " The default blank map, if nothing is being displayed "
    def __init__(self, **kwargs):
        map_options = {
            'center': (-71.40495300292969, 41.82557203489185),
            'zoom': 13,
            'map_type': 'ROADMAP',
            'disable_default_UI': True,
        }
        map_options.update(kwargs)
        super(CommProfilesMap, self).__init__(**map_options)


class GeoRecordMap(CommProfilesMap):
    def __init__(self, georecord):
        def _poly(record):
            fill_color = "#fff"
            if record == georecord:
                fill_color = "#f00"

            poly = google.Polygon(r.geom, fill_color=fill_color, stroke_color="#666", stroke_weight=1)

            hover_data = {'label': record.name}
            poly.add_event('mouseover', 'function(p) { prof.poly_mouseover(p, %s); }' % (json.dumps(hover_data)))
            poly.add_event('mouseout', 'function(p) { prof.poly_mouseout(p); }')

            return poly

        zoom = 13
        if georecord.level.name == 'State':
            zoom = 9
        if georecord.level.name == 'Municipality':
            zoom = 12
        if georecord.level.name == 'Census Tract':
            zoom = 13

        super(GeoRecordMap, self).__init__(
            center=georecord.geom.centroid,
            zoom=zoom,
            polygons=[_poly(r) for r in GeoRecord.objects.filter(parent=georecord.parent, geom__isnull=False)],
        )

class InteractivePolygon(google.Polygon):
    def __init__(self, record, domain,  **kwargs):
        super(InteractivePolygon, self).__init__(record.geom, **kwargs)
        self.record = record
        self.domain = domain

        # We're keeping these as sef.events[0] and self.events[1], because we
        # will modify the mouseover action as hover data is added
        self.add_event(*self._create_mouseover())
        self.add_event('mouseout', 'function(p) { prof.poly_mouseout(p); }')
        self.add_event('click','function(p){prof.poly_click(p,%s);}' % (json.dumps(self._hover_data())))

    def _create_mouseover(self):
        return ('mouseover', 'function(p) { prof.poly_mouseover(p, %s); }' % (json.dumps(self._hover_data())))

    def set_values(self, values):
        self.values = values
        self.events[0] = self._create_mouseover()

    def _hover_data(self):
        hover_data = {'label': self.record.name,'domain':self.domain.slug,'record_slug':self.record.slug,'record_level':self.record.level.slug}
        return hover_data

    @property
    def js_class(self):
        return 'Polygon'

class RecordPolygon(google.Polygon):
    def __init__(self, record, indicator,domain, **kwargs):
        super(RecordPolygon, self).__init__(record.geom, **kwargs)
        self.record = record
        self.indicator = indicator
        self.domain = domain
        self.values = []

        # We're keeping these as sef.events[0] and self.events[1], because we
        # will modify the mouseover action as hover data is added
        self.add_event(*self._create_mouseover())
        self.add_event('mouseout', 'function(p) { prof.poly_mouseout(p); }')
        self.add_event('click','function(p){prof.poly_click(p,%s);}' % (json.dumps(self._hover_data())))

    def _create_mouseover(self):
        return ('mouseover', 'function(p) { prof.poly_mouseover(p, %s); }' % (json.dumps(self._hover_data())))

    def set_values(self, values):
        self.values = values
        self.events[0] = self._create_mouseover()

    def _hover_data(self):
        hover_data = {'label': self.record.name}

        hover_data['domain'] = self.domain.slug
        hover_data['record_slug']=self.record.slug
        hover_data['record_level']=self.record.level.slug
        hover_data['indicator_slug']=self.indicator.slug
        if not self.values:
            return hover_data

        times = set()
        for value in self.values:
            if value.datapoint.is_change():
                times.add('Change')
                hover_data['Change'] = format_number(value.number, data_type=self.indicator.data_type)
            else:
                time_name = value.datapoint.time.name
                times.add(time_name)
                hover_data[time_name] = format_number(value.number,data_type=self.indicator.data_type)

        hover_data['times'] = list(times)


        return hover_data

    @property
    def js_class(self):
        return 'Polygon'

class IndicatorMap(CommProfilesMap):
    def __init__(self, indicator, georecord, domain, GEOS_point=None, place=None):
        """ Display a map of child GeoRecords, colored by this Indicator.

        If there are no children (we're at the Tract level), display siblings.
        """

        self.indicator = indicator
        self.georecord = georecord
        self.domain = domain
	self.markers = []

        if GeoLevel.objects.filter(parent=georecord.level).count() == 0:
            # display siblings
            mapped_records = GeoRecord.objects.filter(parent=georecord.parent, geom__isnull=False)
            center = georecord.geom.centroid
            has_children = False
        else:
            # display children
            mapped_records = GeoRecord.objects.filter(parent=georecord, geom__isnull=False)
            center = mapped_records.collect().centroid
            has_children = True


        if mapped_records.count() == 0:
            return blank_map()

        polylines = None
        if has_children:
            # add an outline of the parent geo
            polylines = [google.Polyline(
                poly,
                stroke_color="#000",
                stroke_weight=2,
                z_index=2
            ) for poly in georecord.geom]

	if GEOS_point:
            marker=google.Marker(geom=GEOS_point, title=place)
            self.markers.append(marker)

        super(IndicatorMap, self).__init__(
            center=center,
            zoom=self._zoom(),
            markers=self.markers,
            polygons=self._polygons(mapped_records),
            polylines=polylines,
        )

    def _polygons(self, records):
        # find the latest non-change time
        latest_time = Time.objects.filter(datapoint__indicator=self.indicator,
            datapoint__record=self.georecord).exclude(name='').order_by('-sort')
        if latest_time:
            latest_time = latest_time[0]
        else:
            latest_time = None

        polys = []
        for record in records:
            stroke_weight = 1
            stroke_color = "#666"
            z_index = 1
            if record == self.georecord:
                stroke_weight = 2
                stroke_color = "#000"
                z_index = 2

            polys.append(RecordPolygon(
                record,
                self.indicator,
				self.domain,
                stroke_color=stroke_color,
                stroke_weight=stroke_weight,
                fill_opacity=0.8,
                z_index=z_index
            ))

        if not latest_time:
            # if we can't determine the time to display, just return outlines
            return polys

        base_values = Value.objects.filter(denominator__isnull=True,
            datapoint__record__in=records, datapoint__indicator=self.indicator
        ).select_related('datapoint', 'datapoint__time')
        data_for_color = base_values.filter(datapoint__time=latest_time)

        self.classes, self.colors = classes_and_colors(
            map(lambda x: float(x.number) if x.number != None else 0, data_for_color)
        )

        def _color(val):
            val = float(val) if val !=None else 0
            for i, (minimum, maximum) in enumerate(self.classes):
                if val >= minimum and val < maximum:
                    return self.colors[i]
            return self.colors[-1]

        # set the color and Value objects for each poly
        for poly in polys:
            record_data = filter(lambda x: x.datapoint.record_id == poly.record.id, base_values)
            if not record_data:
                continue
            poly.set_values(record_data)
            display_value = filter(lambda x: x.datapoint.record_id == poly.record.id, data_for_color)
            if display_value:
                poly.options.fill_color = _color(display_value[0].number)

        return polys

    def _zoom(self):
        if self.georecord.level.name == 'State':
            return 9
        if self.georecord.level.name == 'Municipality':
            return 12
        if self.georecord.level.name == 'Census Tract':
            return 13
        return 13

class GeoSelectMap(CommProfilesMap):
    def __init__(self, georecord, domain, GEOS_point=None, place=None):
        """ Display a map of child GeoRecords,
        If there are no children (we're at the Tract level), display siblings.
        """

        self.georecord = georecord
        self.domain = domain
	self.markers = []

        if GeoLevel.objects.filter(parent=georecord.level).count() == 0:
            # display siblings
            mapped_records = GeoRecord.objects.filter(parent=georecord.parent, geom__isnull=False)
            center = georecord.geom.centroid
            has_children = False
        else:
            # display children
            mapped_records = GeoRecord.objects.filter(parent=georecord, geom__isnull=False)
            center = mapped_records.collect().centroid
            has_children = True


        if mapped_records.count() == 0:
            return blank_map()

        polylines = None
        if has_children:
            # add an outline of the parent geo
            polylines = [google.Polyline(
                poly,
                stroke_color="#444",
                stroke_weight=1.5,
                z_index=2
            ) for poly in georecord.geom]

	if GEOS_point:
            marker=google.Marker(geom=GEOS_point, title=place, clickable='true')
            self.markers.append(marker)

        super(GeoSelectMap, self).__init__(
            center=center,
            zoom=self._zoom(),
            markers=self.markers,
            polygons=self._polygons(mapped_records),
            polylines=polylines,
        )

    def _polygons(self, records):

        polys = []
        for record in records:
            stroke_weight = 1
            stroke_color = "#666"
            z_index = 1
            if record == self.georecord:
                stroke_weight = 1
                stroke_color = "#444"
                z_index = 2

            polys.append(InteractivePolygon(
                record,
				self.domain,
                stroke_color=stroke_color,
                stroke_weight=stroke_weight,
                fill_opacity=0.5,
                z_index=z_index
            ))



        def _color(val):
            val = float(val)
            for i, (minimum, maximum) in enumerate(self.classes):
                if val >= minimum and val < maximum:
                    return self.colors[i]
            return self.colors[-1]

        for poly in polys:

            if poly.record != self.georecord:
                poly.options.fill_color = "#ffde58"
            else:
                poly.options.fill_color = "#56aaff"

        return polys

    def _zoom(self):
        if self.georecord.level.name == 'State':
            return 9
        if self.georecord.level.name == 'Municipality':
            return 12
        if self.georecord.level.name == 'Census Tract':
            return 13
        return 13

def blank_map():
    return CommProfilesMap()


def geo_record_map(georecord, domain, GEOS_point=None, place=None):
	return GeoSelectMap(georecord, domain, GEOS_point, place)


def indicator_map(indicator, georecord, domain, GEOS_point=None, place=None):
    return IndicatorMap(indicator, georecord, domain, GEOS_point, place)
