{% load l10n %}
{% autoescape off %}
{% localize off %}
{% block vars %}var geodjango = {};{% endblock vars %}
{% block functions %}
{% block load %}{{ init_func }} = function(){
    {{ js_module }}.{{ dom_id }} = new google.maps.Map(document.getElementById("{{ dom_id }}"), {{ options.render }});
    {% for marker in markers %}{{ js_module }}.{{ dom_id }}_marker{{ forloop.counter }} = new {{ marker }};
    {{ js_module }}.{{ dom_id }}_marker{{ forloop.counter }}.setMap({{ js_module }}.{{ dom_id }});
    {% for event, action in marker.events %}google.maps.event.addListener({{ js_module }}.{{ dom_id }}_marker{{ forloop.parentloop.counter }}, '{{ event }}', {{ action }});{% endfor %}{% endfor %}
    {% for polygon in polygons %}{{ js_module }}.{{ dom_id }}_poly{{ forloop.counter }} = new {{ polygon }};
    {{ js_module }}.{{ dom_id }}_poly{{ forloop.counter }}.setMap({{ js_module }}.{{ dom_id }});
    {% for event, action in polygon.events %}google.maps.event.addListener({{ js_module }}.{{ dom_id }}_poly{{ forloop.parentloop.counter }}, '{{ event }}', {{ action }});{% endfor %}{% endfor %}
    {% for polyline in polylines %}{{ js_module }}.{{ dom_id }}_polyline{{ forloop.counter }} = new {{ polyline }};
    {{ js_module }}.{{ dom_id }}_polyline{{ forloop.counter }}.setMap({{ js_module }}.{{ dom_id }});
    {% for event, action in polygon.events %}google.maps.event.addListener({{ js_module }}.{{ dom_id }}_polyline{{ forloop.parentloop.counter }}, '{{ event }}', {{ action }});{% endfor %}{% endfor %}
    {% block load_extra %}{% endblock %}
}
{% endblock load %}{% endblock functions %}
{% endlocalize %}
{% endautoescape %}

