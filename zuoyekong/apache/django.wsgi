import os
import sys

app_path='/home/thucloud2/zuoyekong/zuoyekong'
sys.path.append(app_path)
os.chdir(app_path)
os.environ['DJANGO_SETTINGS_MODULE']='zuoyekong.settings'
os.environ.setdefault("DJANGO_SETTING_MODULE","zuoyekong.settings")

import django.core.handlers.wsgi
application=django.core.handlers.wsgi.WSGIHandler()

