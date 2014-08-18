from django.contrib import admin
from userguides.models import *
class AboutPostInline(admin.TabularInline):
    model = AboutPost

class AboutTopicAdmin(admin.ModelAdmin):
    inlines = [AboutPostInline,]
admin.site.register(AboutTopic, AboutTopicAdmin)

admin.site.register(faq)
