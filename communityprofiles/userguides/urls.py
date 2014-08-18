from django.conf.urls import *
from userguides import views

urlpatterns = patterns('',
    url(r'^$', views.about, name="userguides-about"),
    url(r'^FAQ/$', views.faq, name="userguides-FAQ"),
)
