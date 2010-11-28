from django.conf.urls.defaults import *
from django.conf import settings
from django.views.generic.simple import direct_to_template


# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # Example:
    # (r'^onecube/', include('onecube.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),

    (r'^hookbox/', include('hookbox_callbacks.urls')),

    (r'^$', direct_to_template, {'template': 'cube.html'} ),

		(r'^static/(?P<path>[-\w]+.[-\w]+)$', 'django.views.static.serve', {'document_root': settings.STATIC_DOC_ROOT}),

)
