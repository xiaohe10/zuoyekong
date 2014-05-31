# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse
from zuoyekong.settings import ROOT_PATH
from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render

from mobileapp.account.views import is_online
import os
import binascii
from mobileapp.APNSWrapper import *

def application_test(request):
    return render(request, 'app/application/test.html')

def create_application(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_id = request.POST['questionID']
        s = Session()
        userID  = s.get_userID(session_ID=session_ID,session_key=session_key)
        if not userID:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session','errorType':203}))
        try:
            question = Question.objects.get(id = question_id)
            if(question.state != 1):
                return HttpResponse(json.dumps({'result': 'fail', 'msg': 'question has been answered','errorType':302}))
        except:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such question','errorType':301}))
        try:
            old_application = Application.objects.filter(questionId = question_id).get(applicant = userID)
            return HttpResponse(json.dumps({'result': 'success','applicationID':old_application.id}))
        except:
            pass
        #for a in old_applications:
        #    a.delete()
        #    question.applicationNumber -= 1
        #    if question.applicationNumber <= 0:
        #        question.applicationNumber = 0
        application = Application()
        application.applicant = userID
        application.applicationState = 1
        application.questionId = int(question_id.encode('utf-8'))
        question.applicationNumber += 1
        application.save()
        question.save()
        push_to_student_application(question_id)
        return HttpResponse(json.dumps({'result': 'success','applicationID':application.id}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
def push_to_student_application(questionID):
    root = ROOT_PATH
    wrapper = APNSNotificationWrapper(os.path.join(root,'mobileapp','ck.pem'),True,False,True)
    question = Question.objects.get(id = questionID)
    student = User.objects.get(id = question.authorID)
    session = Session.objects.get(userID = student.id)
    token = session.push_token.replace(' ','')
    token = token.replace('<','')
    token = token.replace('>','')
    deviceToken = binascii.unhexlify(token)
    message = APNSNotification()
    message.token(deviceToken)
    message.alert(u'有老师应征回答问题')
    message.setProperty("pushType",31)
    message.badge(1)
    message.sound()
    wrapper.append(message)
    wrapper.connect()
    wrapper.notify()
def cancel_application(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        applicationID = request.POST['applicationID']
        s = Session()
        userID  = s.get_userID(session_ID=session_ID,session_key=session_key)
        if not userID:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session','errorType':203}))
        try:
            application = Application.objects.get(id = applicationID,applicant = userID)
            application.delete()
            return HttpResponse(json.dumps({'result': 'success'}))
        except:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such application or no permission','errorType':304}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))

def list_applications(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_id = request.POST['questionID']
        if request.POST.has_key('limit'):
            limit = request.POST['limit']
        if request.POST.has_key('offset'):
            offset = request.POST['offset']
        if (is_online(session_ID=session_ID,session_key=session_key)):
            try:
                q = Question.objects.get(id=question_id)
            except Exception:
                return HttpResponse(json.dumps({'result': 'fail','errorType': 301, 'msg': 'no such question'}))
            a = Application()
            application_list = a.list_applications_by_question(question_id=question_id)
            return HttpResponse(json.dumps({'result':'success','applicationList':application_list}))
        else:
            return HttpResponse(json.dumps({'result': 'fail','errorType': 203, 'msg': 'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
