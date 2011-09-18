from django.conf.urls.defaults import *

urlpatterns = patterns('hookbox_callbacks.views',
    (r'^connect$', 'connect'),
    (r'^disconnect$', 'disconnect'),
    (r'^create_channel$', 'create_channel'),
    (r'^subscribe$', 'subscribe'),
    (r'^unsubscribe$', 'unsubscribe'),
    (r'^publish$', 'publish'),
)
