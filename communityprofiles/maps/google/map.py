from django.conf import settings
from django.contrib.gis import geos
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe

class GoogleMapException(Exception): pass
from maps.google.overlays import Marker, Polygon, Polyline

# The default Google Maps URL (for the API javascript)
# TODO: Internationalize for Japan, UK, etc.
GOOGLE_MAPS_URL='http://maps.google.com/maps/api/js?sensor=%s'

MAP_TYPES = (
    'HYBRID',
    'ROADMAP',
    'SATELLITE',
    'TERRAIN'
)

class GoogleMapOptions(object):
    def __init__(self, background_color=None, center=None, zoom=None,
                 map_type=None, disable_default_UI=None):
        if map_type is None: map_type = 'HYBRID'
        if not map_type in MAP_TYPES:
            raise GoogleMapException('%s is not a valid map type' % map_type)
        self.map_type = map_type
        self.background_color = background_color
        if zoom is None: zoom = 4
        self.zoom = zoom
        if center is None: center = (0, 0)
        self.center = center
        self.disable_default_UI = disable_default_UI

    def render(self):
        """
        Generates the JavaScript object containing map options.
        """
        opt_lines = []
        opt_lines.append('mapTypeId: google.maps.MapTypeId.%s' % self.map_type)
        if self.background_color:
            opt_lines.append('backgroundColor: %s' % self.background_color)
        if self.disable_default_UI:
            opt_lines.append('disableDefaultUI: %s' % str(self.disable_default_UI).lower())
        opt_lines.append('streetViewControl: false')
        opt_lines.append('center: new google.maps.LatLng(%s, %s)' % (self.center[1], self.center[0]))
        opt_lines.append('zoom: %s' % self.zoom)
        opt_lines.append('panControl: true')
        opt_lines.append('zoomControl: true')
        return mark_safe("{%s}" % ','.join(opt_lines))


class GoogleMap(object):
    "A class for generating Google Maps v3 JavaScript."

    def __init__(self, api_url=None, sensor=False, js_module='geodjango',
                 template='maps/google/google-map.js', center=None, zoom=None,
                 dom_id='map', extra_context={}, markers=None, polygons=None,
                 polylines=None, map_type=None, disable_default_UI=None):
        self.sensor = sensor
        self.template = template
        self.js_module = js_module
        self.dom_id = dom_id
        self.extra_context = extra_context
        
        if zoom is None: zoom = 4
        if center is None: center = (0, 0)
        self.options = GoogleMapOptions(center=center, zoom=zoom, map_type=map_type, disable_default_UI=disable_default_UI)

        # Can specify the API URL in the `api_url` keyword.
        if not api_url:
            self.api_url = mark_safe(getattr(settings, 'GOOGLE_MAPS_URL', GOOGLE_MAPS_URL) % str(self.sensor).lower())
        else:
            self.api_url = api_url

        # Does the user want any GMarker, GPolygon, and/or GPolyline overlays?
        overlay_info = [[Marker, markers, 'markers'],
                        [Polygon, polygons, 'polygons'],
                        [Polyline, polylines, 'polylines']]

        for overlay_class, overlay_list, varname in overlay_info:
            setattr(self, varname, [])
            if overlay_list:
                for overlay in overlay_list:
                    if isinstance(overlay, overlay_class):
                        getattr(self, varname).append(overlay)
                    else:
                        getattr(self, varname).append(overlay_class(overlay))

    
    def render(self):
        """
        Generates the JavaScript necessary for displaying this Google Map.
        """
        params = {
                  'dom_id' : self.dom_id,
                  'js_module' : self.js_module,
                  'init_func' : self.init_func,
                  'options' : self.options,
                  'markers' : self.markers,
                  'polygons': self.polygons,
                  'polylines': self.polylines,
                  }
        params.update(self.extra_context)
        return render_to_string(self.template, params)

    @property
    def js(self):
        "Returns only the generated Google Maps JavaScript (no <script> tags)."
        return self.render()

    @property
    def api_script(self):
        "Returns the <script> tag for the Google Maps API javascript."
        return mark_safe('<script src="%s" type="text/javascript"></script>' % (self.api_url, ))

    @property
    def scripts(self):
        "Returns all <script></script> tags required with Google Maps JavaScript."
        return mark_safe('%s\n  <script type="text/javascript">\n//<![CDATA[\n%s//]]>\n  </script>' % (self.api_script, self.js))

    @property
    def init_func(self):
        return mark_safe("%s.%s_load" % (self.js_module, self.dom_id))
