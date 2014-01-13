# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render
from zuoyekong.settings import ROOT_PATH
from mobileapp.account.views import is_online
from mobileapp.question.views import verify_access_2_question
from mobileapp.APNSWrapper import *
import binascii
import os.path
from pyDes import *

def dialog_test(request):
    return render(request, 'dialog/test.html')

def create_dialog(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        applicationID = request.POST['applicationID']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))

    s = Session()
    userID  = s.get_userID(session_ID=session_ID,session_key=session_key)
    if not userID:
        return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session','errorType':203}))

    try:
        application = Application.objects.get(id = applicationID)
        question = Question.objects.get(id = application.questionId,authorID = userID)
        old_dialogs = Dialog.objects.filter(questionId = question.id, studentId = userID)
        for d in old_dialogs:
            d.delete()
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such application','errorType':304}))
    try:
        dialog = Dialog(studentId = userID,teacherId = application.applicant,questionId = question.id,state=1,all_time=0,charging_time=0)

        dialog.generate_dialog_session()
        dialog.save()
        try:
            push_call_request_2_teacher(application.applicant,question,dialog,userID)
        except:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'push call to teacher fail','errorType':403}))
        return HttpResponse(json.dumps({'result':'success','dialogID':dialog.id,'dialogSession':dialog.dialogSession}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'msg': 'unkown error','errorType':501}))

def accept_dialog(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        dialogID = request.POST['dialogID']
        dialogKey = request.POST['dialogKey']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))

    try:
        session = Session.objects.get(session_ID = session_ID,session_key = session_key)
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 203, 'msg': 'no such session'}))
    try:
        dialog = Dialog.objects.get(id = dialogID,teacherId = session.userID,dialogSession = dialogKey,state = 1)
        try:
            cloopen_accounts = CloopenAccount.objects.filter(state = 0)[0:2]
            for c in cloopen_accounts:
                #c.state = 0
                c.save()
            try:
                push_call_response_2_student(dialog,cloopen_accounts[1])
                return HttpResponse(json.dumps({'result':'success','cloopenAccount':cloopen_accounts[0].cloudAccount,'cloopenSecret':cloopen_accounts[0].cloudSecret,'voIPAccount':cloopen_accounts[0].voIPAccount,'voIPSecret':cloopen_accounts[0].voIPSecret}))
            except:
                return HttpResponse(json.dumps({'result': 'fail', 'msg': 'push acceptance to student fail','errorType':404}))
        except:
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 306, 'msg': 'no cloopen accont'}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 402, 'msg': 'no such dialog or out time'}))

def cancel_call(request):
    return True

def reject_call(request):
    return True

def put_cloopen_account(request):
    try:
        cloudAcount = request.POST['cloudAcount']
        cloudSecret = request.POST['cloudSecret']
        voIPAccount = request.POST['voIPAccount']
        voIPSecret = request.POST['voIPSecret']
    except:
        return HttpResponse('wrong request paraments')

    try:
        CA = CloopenAccount()
        CA.cloudAccount = cloudAcount
        CA.cloudSecret = cloudSecret
        CA.voIPAccount = voIPAccount
        CA.voIPSecret = voIPSecret
        CA.state = 0
        CA.save()
        return HttpResponse('ok '+CA.id.__str__())
    except:
        return HttpResponse('cloopen account save fail')


def validate(request):
    try:
        print request
        dialogID = request.POST['dialogId']
        dialogKey = request.POST['dialogKey']
        try:
            d = Dialog.objects.get(id = dialogID,dialogSession = dialogKey)
            return HttpResponse('yes')
        except:
            return HttpResponse('no')
    except:
        return HttpResponse('wrong')

def commit(request):
    try:
        dialogID = request.POST['dialogId']
        dialogKey = request.POST['dialogKey']
        startTime = request.POST['startTime']
        endTime = request.POST['endTime']
        allTime = request.POST['allTime']
        feeTime = request.POST['feeTime']
        signature = request.POST['signature']
    except:
        return HttpResponse('wrong')
    k = des("DESCRYPT", CBC, "\0\0\0\0\0\0\0\0", pad=None, padmode=PAD_PKCS5)
    print k.decrypt(signature,padmode=PAD_PKCS5)
    return HttpResponse('yes')


def push_call_request_2_teacher(teacherID,question,dialog,userID):
    root = ROOT_PATH.replace('/','\\')
    wrapper = APNSNotificationWrapper(os.path.join(root,'mobileapp','ck.pem'), True,True,True)
    session = Session.objects.get(userID = teacherID)
    token = session.push_token.replace(' ','')
    token = token.replace('<','')
    token = token.replace('>','')
    deviceToken = binascii.unhexlify(token)
    # create message
    message = APNSNotification()
    message.token(deviceToken)
    message.alert(u'a dialog request')
    message.setProperty("questioninfo",[question.id,question.title,question.description,question.authorRealName,'media'+question.thumbnails])
    message.setProperty("dialoginfo",[dialog.id,dialog.dialogSession])
    message.badge(1)
    message.sound()
    print message.__str__()
    # add message to tuple and send it to APNS server
    wrapper.append(message)
    #wrapper.connect()
    #wrapper.notify()

def push_call_response_2_student(dialog,cloopen_account):
    root = ROOT_PATH.replace('/','\\')
    wrapper = APNSNotificationWrapper(os.path.join(root,'mobileapp','ck.pem'), True,True,True)
    session = Session.objects.get(userID = dialog.studentId)
    token = session.push_token.replace(' ','')
    token = token.replace('<','')
    token = token.replace('>','')
    deviceToken = binascii.unhexlify(token)
    # create message
    message = APNSNotification()
    message.token(deviceToken)
    message.alert(u'a dialog response')
    message.setProperty("dialoginfo",[dialog.id,dialog.dialogSession])
    message.setProperty("cloopenAccount",[cloopen_account.cloudAccount,cloopen_account.cloudSecret,cloopen_account.voIPAccount,cloopen_account.voIPSecret])
    message.badge(1)
    message.sound()
    print message.__str__()
    # add message to tuple and send it to APNS server
    wrapper.append(message)
    #wrapper.connect()
    #wrapper.notify()

def get_recent_teacher(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        #todo question exist?
        if request.POST.has_key('limit'):
            limit  = request.POST['limit']
            if not limit:
                limit = 5
        else:
            limit = 5
        if request.POST.has_key('offset'):
            offset  = request.POST['offset']
            if not offset:
                offset = 0
        else:
            offset = 0
        if is_online(session_ID=session_ID, session_key=session_key):
            try:
                teachers = User.objects.filter(userType = 2)[int(offset):int(offset)+int(limit)]
            except:
                try:
                    teachers = User.objects.filter(userType = 2)[int(offset):]
                except:
                    teachers = []
            #todo recommend teacher
            teacher_list = []
            for t in teachers:
                teacher = {}
                teacher['teacherID'] = t.id
                teacher['realname'] = t.realname
                teacher['userType'] = t.userType
                teacher['grade'] = t.grade
                teacher['school'] = t.school
                teacher['description'] = t.description
                if t.headImage:
                    teacher['headImage'] = '/media/'+t.headImage.__str__()
                else:
                    teacher['headImage'] = ''
                teacher['identify'] = t.identify
                teacher_list.append(teacher)
            return HttpResponse(json.dumps({'result':'success','recommendTeacherList':teacher_list}))
        else:
            return HttpResponse(json.dumps({'result': 'fail','errorType':203, 'msg': 'no such session'}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))

