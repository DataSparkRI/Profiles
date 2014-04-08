from decimal import Decimal

from django.utils.safestring import mark_safe
from django.contrib.gis.geos import fromstr, Point
from django.contrib.gis.geos import Polygon as geos_Polygon
from django.contrib.gis.geos import MultiPolygon as geos_MultiPolygon
from django.contrib.gis.geos import LinearRing as geos_LinearRing
from django.contrib.gis.geos import LineString as geos_LineString

# Valid animation types. 
# http://code.google.com/apis/maps/documentation/javascript/reference.html#Animation
ANIMATIONS = (
    'BOUNCE',
    'DROP',
)


class OverlayBase(object):
    def __init__(self):
        self.events = []

    def __unicode__(self):
        "The string representation is the JavaScript API call."
        return mark_safe('google.maps.%s(%s)' % (self.js_class, self.js_params))
    
    @property
    def js_class(self):
        return self.__class__.__name__
    
    def latlng_from_coords(self, coords):
        "Generates a JavaScript array of GLatLng objects for the given coordinates."
        return '[%s]' % ','.join(['new google.maps.LatLng(%s,%s)' % (y, x) for x, y in coords])
    
    def add_event(self, event, action):
        "Attaches a GEvent to the overlay object."
        self.events.append((event, action, ))

class MarkerOptions(object):
    """ A Python wrapper for the google.maps.MarkerOptions spec. For more
        information please see the Google Maps API Reference:
        http://code.google.com/apis/maps/documentation/javascript/reference.html#MarkerOptions
    """
    def __init__(self, position, animation=None, clickable=None, cursor=None, draggable=None,
                 flat=None, icon=None, optimized=None, raise_on_drag=None,
                 shadow=None, title=None, visible=None, z_index=None):
        if not animation is None and not animation in ANIMATIONS:
            raise GoogleMapException('%s is not a valid map type' % map_type)
        self.animation = animation
        self.clickable = clickable
        self.cursor = cursor
        self.draggable = draggable
        self.flat = flat
        self.icon = icon
        self.optimized = optimized
        self.position = position
        self.raise_on_drag = raise_on_drag
        self.shadow = shadow
        self.title = title
        self.visible = visible
        self.z_index = z_index
        if not self.z_index is None:
            self.z_index = int(z_index)

        super(MarkerOptions, self).__init__()

    def render(self):
        """
        Generates the JavaScript object containing marker options.
        """
        opt_lines = []
        if not self.animation is None:
            opt_lines.append('animation: google.maps.Animation.%s' % self.animation)
        if not self.clickable is None:
            opt_lines.append('clickable: %s' % str(self.clickable).lower())
        if not self.cursor is None:
            opt_lines.append("cusor: '%s'" % self.cursor)
        if not self.draggable is None:
            opt_lines.append('draggable: %s' % str(self.draggable).lower())
        if not self.flat is None:
            opt_lines.append('flat: %s' % str(self.flat).lower())
        if not self.icon is None:
            opt_lines.append('icon: "%s"' % self.icon)
        if not self.optimized is None:
            opt_lines.append('optimized: %s' % str(self.optimized).lower())
        opt_lines.append('position: new google.maps.LatLng(%s, %s)' % (self.position[1], self.position[0]))
        if not self.raise_on_drag is None:
            opt_lines.append('raiseOnDrag: %s' % str(self.raise_on_drag).lower())
        if not self.shadow is None:
            opt_lines.append('shadow: "%s"' % self.shadow)
        if not self.title is None:
            opt_lines.append('title: "%s"' % self.title)
        if not self.visible is None:
            opt_lines.append('visible: %s' % str(self.visible).lower())
        if not self.z_index is None:
            opt_lines.append('zIndex: %d' % self.z_index)
        return mark_safe("{%s}" % ','.join(opt_lines))


class Marker(OverlayBase):
    """
    A Python wrapper for the Google google.maps.Marker object.  For more information
    please see the Google Maps API Reference:
     http://code.google.com/apis/maps/documentation/javascript/reference.html#Marker

    Example:

      from django.shortcuts import render_to_response
      from django.contrib.gis.maps.google.overlays import GMarker, GEvent

      def sample_request(request):
          marker = GMarker('POINT(101 26)')
          event = GEvent('click',
                         'function() { location.href = "http://www.google.com"}')
          marker.add_event(event)
          return render_to_response('mytemplate.html',
                 {'google' : GoogleMap(markers=[marker])})
    """
    def __init__(self, geom, animation=None, clickable=None, cursor=None, draggable=None,
                 flat=None, icon=None, optimized=None, raise_on_drag=None,
                 shadow=None, title=None, visible=None, z_index=None):
        """
        The Marker object may initialize on GEOS Points or a parameter
        that may be instantiated into a GEOS point.  Keyword options map to
        MarkerOptions.

        Keyword Options:
         title:
           Title option for GMarker, will be displayed as a tooltip.

         draggable:
           Draggable option for GMarker, disabled by default.
        """
        # If a GEOS geometry isn't passed in, try to construct one.
        if isinstance(geom, basestring): geom = fromstr(geom)
        if isinstance(geom, (tuple, list)): geom = Point(geom)
        if isinstance(geom, Point):
            self.position = geom.coords
        else:
		raise TypeError('Marker may only initialize on GEOS Point geometry.')

        self.options = MarkerOptions(self.position, animation=animation, 
            clickable=clickable, cursor=cursor, draggable=draggable, flat=flat, 
            icon=icon, optimized=optimized, raise_on_drag=raise_on_drag, 
            shadow=shadow, title=title, visible=visible, z_index=z_index)
        super(Marker, self).__init__()

    @property
    def js_params(self):
        return '%s' % self.options.render()

class PolygonOptions(object):
    """ A Python wrapper for the google.maps.PolygonOptions spec. For more
        information please see the Google Maps API Reference:
        http://code.google.com/apis/maps/documentation/javascript/reference.html#PolygonOptions
    """
    def __init__(self, points, clickable=None, fill_color=None, fill_opacity=None, geodesic=None, stroke_color=None,
                 stroke_opacity=None, stroke_weight=None, z_index=None):
        self.clickable = clickable
        self.fill_color = fill_color
        self.fill_opacity = fill_opacity
        if not self.fill_opacity is None:
            self.fill_opacity = Decimal(str(fill_opacity))
            if self.fill_opacity > Decimal("1.0") or self.fill_opacity < Decimal("0.0"):
                raise AttributeError('fill_opacity must be between 0 and 1')
        self.geodesic = geodesic
        self.stroke_color = stroke_color
        self.stroke_opacity = stroke_opacity
        if not self.stroke_opacity is None:
            self.stroke_opacity = Decimal(str(stroke_opacity))
            if self.stroke_opacity > Decimal("1.0") or self.stroke_opacity < Decimal("0.0"):
                raise AttributeError('stroke_opacity must be between 0 and 1')
        self.stroke_weight = stroke_weight
        if not self.stroke_weight is None:
            self.stroke_weight = int(stroke_weight)
        self.z_index = z_index
        if not self.z_index is None:
            self.z_index = int(z_index)
        self.points = points
        super(PolygonOptions, self).__init__()

    def render(self):
        """
        Generates the JavaScript object containing map options. 
        """
        opt_lines = []
        if not self.clickable is None:
            opt_lines.append('clickable: %s' % str(self.clickable).lower())
        if not self.fill_color is None:
            opt_lines.append("fillColor: '%s'" % self.fill_color)
        if not self.fill_opacity is None:
            opt_lines.append('fillOpacity: %s' % self.fill_opacity)
        if not self.geodesic is None:
            opt_lines.append('flat: %s' % str(self.geodesic).lower())
        if not self.stroke_color is None:
            opt_lines.append('strokeColor: "%s"' % self.stroke_color)
        if not self.stroke_opacity is None:
            opt_lines.append('strokeOpacity: %s' % self.stroke_opacity)
        if not self.stroke_weight is None:
            opt_lines.append('strokeWeight: %s' % self.stroke_weight)
        if not self.z_index is None:
            opt_lines.append('zIndex: %d' % self.z_index)
        if hasattr(self.points, '__iter__'):
            opt_lines.append('paths: [%s]' % ','.join(self.points))
        else:
            opt_lines.append('paths: %s' % self.points)
        return mark_safe("{%s}" % ','.join(opt_lines))

class Polygon(OverlayBase):
    """
    A Python wrapper for the Google GPolygon object.  For more information
    please see the Google Maps API Reference:
     http://code.google.com/apis/maps/documentation/javascript/reference.html#Polygon
    """
    def __init__(self, poly, clickable=None, fill_color=None, fill_opacity=None, 
                 geodesic=None, stroke_color=None, stroke_opacity=None, 
                 stroke_weight=None, z_index=None):
        """
        The GPolygon object initializes on a GEOS Polygon or a parameter that
        may be instantiated into GEOS Polygon.  Please note that this will not
        depict a Polygon's internal rings. Keyword options map to
        PolygonOptions.
        """
        if isinstance(poly, basestring): poly = fromstr(poly)
        if isinstance(poly, (tuple, list)): poly = Polygon(poly)
        if not isinstance(poly, (geos_Polygon, geos_MultiPolygon)):
            raise TypeError('Polygon may only initialize on GEOS Polygons or MultiPolygons.')
        
        # Translating the coordinates into a JavaScript array of
        # Google `google.maps.LatLng` objects.
        if isinstance(poly, geos_Polygon):
            self.points = self.latlng_from_coords(poly.shell.coords)
        if isinstance(poly, geos_MultiPolygon):
            self.points = [self.latlng_from_coords(poly.shell.coords) for poly in poly]

        self.options = PolygonOptions(self.points, clickable=clickable, 
            fill_color=fill_color, fill_opacity=fill_opacity, geodesic=geodesic, 
            stroke_color=stroke_color, stroke_opacity=stroke_opacity, 
            stroke_weight=stroke_weight, z_index=z_index)
        super(Polygon, self).__init__()

    @property
    def js_params(self):
        return '%s' % self.options.render()

class PolylineOptions(object):
    """ A Python wrapper for the google.maps.PolygonOptions spec. For more
        information please see the Google Maps API Reference:
        http://code.google.com/apis/maps/documentation/javascript/reference.html#PolygonOptions
    """
    def __init__(self, points, clickable=None, fill_color=None, fill_opacity=None, geodesic=None, stroke_color=None,
                 stroke_opacity=None, stroke_weight=None, z_index=None):
        self.clickable = clickable
        self.geodesic = geodesic
        self.stroke_color = stroke_color
        self.stroke_opacity = stroke_opacity
        if not self.stroke_opacity is None:
            self.stroke_opacity = Decimal(str(stroke_opacity))
            if self.stroke_opacity > Decimal("1.0") or self.stroke_opacity < Decimal("0.0"):
                raise AttributeError('stroke_opacity must be between 0 and 1')
        self.stroke_weight = stroke_weight
        if not self.stroke_weight is None:
            self.stroke_weight = int(stroke_weight)
        self.z_index = z_index
        if not self.z_index is None:
            self.z_index = int(z_index)
        self.points = points
        super(PolylineOptions, self).__init__()

    def render(self):
        """
        Generates the JavaScript object containing map options. 
        """
        opt_lines = []
        if not self.clickable is None:
            opt_lines.append('clickable: %s' % str(self.clickable).lower())
        if not self.geodesic is None:
            opt_lines.append('flat: %s' % str(self.geodesic).lower())
        if not self.stroke_color is None:
            opt_lines.append('strokeColor: "%s"' % self.stroke_color)
        if not self.stroke_opacity is None:
            opt_lines.append('strokeOpacity: %s' % self.stroke_opacity)
        if not self.stroke_weight is None:
            opt_lines.append('strokeWeight: %s' % self.stroke_weight)
        if not self.z_index is None:
            opt_lines.append('zIndex: %d' % self.z_index)
        opt_lines.append('path: %s' % self.points)
        return mark_safe("{%s}" % ','.join(opt_lines))


class Polyline(OverlayBase):
    """
    A Python wrapper for the Google Polyline object.  For more information
    please see the Google Maps API Reference:
     http://code.google.com/apis/maps/documentation/javascript/reference.html#Polyline
    """
    def __init__(self, poly, clickable=None, fill_color=None, fill_opacity=None, 
                 geodesic=None, stroke_color=None, stroke_opacity=None, 
                 stroke_weight=None, z_index=None):
        """
        The Polyline object may be initialized on GEOS LineStirng, LinearRing,
        and Polygon objects (internal rings not supported) or a parameter that
        may instantiated into one of the above geometries.

        Keyword Options:


        """
        if isinstance(poly, basestring): poly = fromstr(poly)
        if isinstance(poly, (tuple, list)): poly = Polygon(poly)
        if not isinstance(poly, (geos_Polygon, geos_MultiPolygon, geos_LineString, geos_LinearRing)):
            raise TypeError('Polyline may only initialize on GEOS LineString, LinearRing, and/or Polygon geometries.')
        
        # Translating the coordinates into a JavaScript array of
        # Google `google.maps.LatLng` objects.
        if isinstance(poly, (geos_LineString, geos_LinearRing)):
            self.points = self.latlng_from_coords(poly.coords)
        if isinstance(poly, geos_Polygon):
            self.points = self.latlng_from_coords(poly.shell.coords)
        
        self.options = PolylineOptions(self.points, clickable=clickable, 
            geodesic=geodesic, stroke_color=stroke_color, 
            stroke_opacity=stroke_opacity, stroke_weight=stroke_weight, 
            z_index=z_index)
        super(Polyline, self).__init__()


    @property
    def js_params(self):
        return '%s' % self.options.render()
