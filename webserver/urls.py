from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    (r'^hookbox/', include('hookbox_callbacks.urls')),

    (r'^$', direct_to_template, {'template': 'homepage.html'} ),
    (r'^super_sekret_cube$', direct_to_template, {'template': 'cube.html'} ),
    (r'^admin_cube$', direct_to_template, {'template': 'admin_cube.html'} ),
    (r'^cube_inspector$', direct_to_template, {'template': 'cube_inspector.html'} ),

    (r'^static/(?P<path>[-\w]+.[-\w]+)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),

)
