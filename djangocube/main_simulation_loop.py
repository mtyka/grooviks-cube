#!/usr/bin/python
"""To get this to run, you need to set two environment variables:

export DJANGO_SETTINGS_MODULE=djangocube.settings
export PYTHONPATH=.:..:$PYTHONPATH
"""

import datetime
import time
from syncstate.models import KeyFrame

while True:
    kf, is_newly_created = KeyFrame.objects.get_or_create(pk=1)
    now = datetime.datetime.now()
    print kf
    kf.set_swirly( now.second )
    kf.save()
    time.sleep(3)

