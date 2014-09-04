from django.conf.urls import *
from userguides import views

urlpatterns = patterns('',
    url(r'^$', views.about, name="userguides-about"),
    url(r'^FAQ/$', views.faq, name="userguides-FAQ"),
    url(r'stay_in_touch$',views.stay, name="userguides-stay"),
)
