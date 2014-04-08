from haystack.indexes import *
from profiles.models import Indicator
#from data_displays.models import DataDisplay


class IndicatorIndex(SearchIndex, Indexable):
    text = CharField(document=True, use_template=True)
    records = MultiValueField()  # we need to track what records an indicator is available for
    domains = MultiValueField()

    def get_model(self):
        return Indicator

    def prepare_records(self, obj):
        result = []
        for level in obj.levels.all():
            result.extend(map(lambda r: r.id, level.georecord_set.all()))
        return result

    def prepare_domains(self, obj):
        return map(lambda d: d.id, obj.data_domains.all())

#site.register(Indicator, IndicatorIndex)


#class DataDisplayIndex(SearchIndex):
#    text = CharField(document=True, use_template=True)

#site.register(DataDisplay, DataDisplayIndex)


# class DataDisplayIndex(SearchIndex):
#     text = CharField(document=True, use_template=True)
#     record_id = IntegerField()
#     indicator_id = IntegerField()
#     domains = MultiValueField()

#     def prepare_record_id(self, obj):
#         if obj.record:
#             return obj.record.id
#         else:
#             return -1

#     def prepare_indicator_id(self, obj):
#         if obj.indicator:
#             return obj.indicator.id
#         else:
#             return -1

#     def prepare_domains(self, obj):
#         result = []
#         if obj.indicator:
#             result.append(obj.indicator.default_domain().id)
#         result.extend(map(lambda d: d.id, obj.template.domains.all()))
#         return result
# site.register(DataDisplay, DataDisplayIndex)
