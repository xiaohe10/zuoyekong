#-*-coding:utf-8-*-
import os
import sys
import django.core.handlers.wsgi

os.environ['DJANGO_SETTINGS_MODULE']='zuoyekong.settings'
app_apth='/home/xiaohe/zuoyekong/zuoyekong'
sys.path.append(app_apth)
application=django.core.handlers.wsgi.WSGIHandler()

