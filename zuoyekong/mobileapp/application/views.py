# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render

from mobileapp.account.views import is_online

def application_test(request):
    return render(request, 'application/test.html')

def create_application(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_id = request.POST['questionID']
        s = Session()
        phone  = s.get_user_phone(session_ID=session_ID,session_key=session_key)
        if not phone:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session','errorType':203}))
        try:
            user = User.objects.get(phone=phone)
        except Exception:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such user'}))
        application = Application()
        application.applicant = user.id
        application.state = 'unread'
        application.qustionId = question_id
        application.save()
        return HttpResponse(json.dumps({'result': 'success','applicationID':application.id}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'wrong request params'}))

def cancel_application(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        application_id = request.POST['applicationID']
        s = Session()
        phone  = s.get_user_phone(session_ID=session_ID,session_key=session_key)
        if not phone:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session'}))
        try:
            user = User.objects.get(phone=phone)
        except Exception:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such user'}))
        try:
            application = Application.objects.get(id=application_id,applicant=user.id)
            application.delete()
            return HttpResponse(json.dumps({'result': 'success'}))
        except Exception:
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'no such application or cannot access to it'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'wrong request params'}))

def list_applications(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_id = request.POST['questionID']
        if (is_online(session_ID=session_ID,session_key=session_key)):
            try:
                q = Question.objects.get(id=question_id)
            except Exception:
                return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such question'}))
            a = Application()
            application_list = a.list_applications_by_question(question_id=question_id)
            return HttpResponse(json.dumps({'result':'success','application_list':application_list}))
        else:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'wrong request params'}))
