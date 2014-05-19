# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render
from zuoyekong.settings import SITE_URL
from PIL import Image
import os
from zuoyekong.settings import MEDIA_ROOT
from django.db.models.fields.files import FileField
import mobileapp.account.views
from django.http import HttpResponseRedirect
from django.db.models import Q

def pull_message(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 203, 'msg': 'no such session'}))
    try:
        s = Session()
        userID  = s.get_userID(session_ID=sessionID,session_key=sessionKey)
        if not userID:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session','errorType':203}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session','errorType':203}))
    try:
        p = PushMessage()
        if request.POST.has_key('pushType'):
            pushType = request.POST['pushType']
            r = p.get_message_by_type(userID=userID,pushType=pushType)
            return HttpResponse(json.dumps({'result':'success','messageList':r}))
        else:
            r = p.get_message_by_type(userID=userID)
            return HttpResponse(json.dumps({'result':'success','messageList':r}))
    except:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'fail to get message'}))