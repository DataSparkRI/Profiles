from haystack.indexes import *
from data_displays.models import DataDisplay


class DataDisplayIndex(SearchIndex, Indexable):
    text = CharField(document=True, use_template=True)
    record_id = IntegerField()

    def get_model(self):
        return DataDisplay

    def prepare_record_id(self,obj):
        if obj.record:
            return obj.record.id
        else:
            return -1

