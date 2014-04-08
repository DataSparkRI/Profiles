from django.core.management.base import BaseCommand, CommandError
from data_displays.models import DataDisplayTemplate

class Command(BaseCommand):

    def handle(self, *args, **options):
        display = DataDisplayTemplate.objects.all()[0]
        display.render_display()
        