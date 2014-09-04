from django.contrib import admin
from userguides.models import *
import csv
from django.http import HttpResponse

#------------- ACTIONS -----------------#
def export_user_info(modeladmin, request, queryset):
    response = HttpResponse(content_type="application/csv")
    response['Content-Disposition'] = 'attachment; filename="stay_in_touch_users.csv"'
    writer = csv.writer(response)
    writer.writerow(['Name', 'E-Mail', 'Create-Time'])
    if len(queryset) == 1 : #export all user info
       total = StayInTouchUser.objects.all()
       for q in total:
           writer.writerow([q.name, q.email, q.create_time])

    else:
       for q in queryset:
           writer.writerow([q.name, q.email, q.create_time])
    return response
export_user_info.short_description = \
    "Export User Information (select 1 user means export all users)"

class AboutPostInline(admin.TabularInline):
    model = AboutPost

class AboutTopicAdmin(admin.ModelAdmin):
    inlines = [AboutPostInline,]

class StayInTouchUserAdmin(admin.ModelAdmin):
    list_display = ('name','email','create_time',)
    actions = [export_user_info] 

admin.site.register(StayInTouchUser, StayInTouchUserAdmin)

admin.site.register(AboutTopic, AboutTopicAdmin)

admin.site.register(faq)
