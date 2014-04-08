from data_displays.models import DataDisplayTemplate
def admin_generate_data_display(ddt_id):
    from profiles.tasks import generate_data_display
    # grab the ddt
    ddt = DataDisplayTemplate.objects.get(pk=int(ddt_id))
    generate_data_display.delay(ddt)
    return "Kicked off rendering for %s" % ddt.title
