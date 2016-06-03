from django.conf.urls import url

from . import views

urlpatterns = [
    # index
    url(r'^$', views.index, name='index'),

    # monitor
    url(r'^monitor/$', views.monitor, name='monitor'),
    url(r'^monitor/(?P<controller>.+)/(?P<select>.+)/(?P<timerange>.+)/(?P<plotnumber>.+)/$', views.scopedraw, name='scopedraw'),

    # detail
    url(r'^(?P<config_controller>.+)/$', views.detail, name='detail'),



]
