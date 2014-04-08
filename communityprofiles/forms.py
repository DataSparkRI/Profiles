from django.forms.forms import NON_FIELD_ERRORS
from django.forms.util import ErrorList
from django.utils.encoding import force_unicode
from django.utils.html import conditional_escape
from django.utils.safestring import mark_safe

import floppyforms as forms



class NonFieldErrorList(ErrorList):
    def as_ul(self):
        if not self: return u''
        return mark_safe(u'<ul class="errorlist nonfield">%s</ul>'
                % ''.join([u'<li>%s</li>' % conditional_escape(force_unicode(e)) for e in self]))



class NonFieldErrorsMixin(object):
    """
    Form mixin class to give non-field-errors a "nonfield" class on the
    error-list.

    """
    def _clean_form(self):
        try:
            self.cleaned_data = self.clean()
        except forms.ValidationError, e:
            self._errors[NON_FIELD_ERRORS] = NonFieldErrorList(e.messages)



class LabelPlaceholdersMixin(object):
    """
    Form mixin class to give all widgets a "placeholder" attribute the same as
    their label.

    """
    def __init__(self, *args, **kwargs):
        super(LabelPlaceholdersMixin, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            field.widget.attrs.setdefault("placeholder", field.label)



class FloppyWidgetsMixin(object):
    """
    Form mixin class to replace standard Django form widgets with the
    floppyforms HTML5 template-driven widget equivalent.

    Also looks up a possible explicit widget-class override in
    ``self.widget_classes``.

    """
    widget_classes = {}

    def __init__(self, *args, **kwargs):
        super(FloppyWidgetsMixin, self).__init__(*args, **kwargs)
        for fieldname, field in self.fields.items():
            widget = field.widget
            new = None
            if fieldname in self.widget_classes:
                new = self.widget_classes[fieldname](widget.attrs)
            else:
                floppy_class = getattr(forms, widget.__class__.__name__, None)
                if floppy_class is not None:
                    new = floppy_class(widget.attrs)
            if new is not None:
                new.is_required = widget.is_required
                field.widget = new



class BareTextarea(forms.Textarea):
    """
    A Textarea with no rows or cols attributes.

    """
    def __init__(self, *args, **kwargs):
        super(BareTextarea, self).__init__(*args, **kwargs)
        self.attrs = {}

