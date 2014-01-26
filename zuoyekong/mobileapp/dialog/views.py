# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse
from django.shortcuts import redirect
from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render
from zuoyekong.settings import ROOT_PATH
from mobileapp.account.views import is_online
from mobileapp.question.views import verify_access_2_question
from mobileapp.APNSWrapper import *
import binascii
import hashlib
import os.path
from pyDes import *
import base64

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
        teacher = User.objects.get(id = application.applicant)
        if teacher.activeState == 2:
            return HttpResponse(json.dumps({'result':'fail','msg':'teacher is busy','errorType':405}))
                
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
            if cloopen_accounts == []:

                return HttpResponse(json.dumps({'result': 'fail', 'errorType': 306, 'msg': 'no cloopen accont'}))
            print cloopen_accounts
            for c in cloopen_accounts:
                c.state = 1
                c.dialogID =dialogID
                c.save()
            try:
                try:
                    push_call_response_2_student(dialog,cloopen_accounts[1],cloopen_accounts[0].voIPAccount)
                    teacherID = Session.objects.get(session_ID = session_ID,session_key = session_key).userID
                    teacher  = User.objects.get(id = teacherID)
                    teacher.activeState = 2
                    teacher.save()
                except:
                    print "teacher active state change fail"
                return HttpResponse(json.dumps({'result':'success','cloopenAccount':cloopen_accounts[0].cloudAccount,'cloopenSecret':cloopen_accounts[0].cloudSecret,'voIPAccount':cloopen_accounts[0].voIPAccount,'voIPSecret':cloopen_accounts[0].voIPSecret,'voIPAccount2':cloopen_accounts[1].voIPAccount}))
            except:
                return HttpResponse(json.dumps({'result': 'fail', 'msg': 'push acceptance to student fail','errorType':404}))
        except:
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 306, 'msg': 'no cloopen accont'}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 402, 'msg': 'no such dialog or out time'}))

def cancel_call(request):
    return True

def reject_call(request):
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
            push_call_reject_2_student(dialog)
            return HttpResponse(json.dumps({'result':'success'}))
        except:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'push acceptance to student fail','errorType':404}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 402, 'msg': 'no such dialog or out time'}))

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
        CA.dialogID = 0
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
        print request
        dialogID = request.POST['dialogId']
        dialogKey = request.POST['dialogKey']
        startTime = request.POST['startTime']
        endTime = request.POST['endTime']
        allTime = request.POST['allTime']
        feeTime = request.POST['feeTime']
        signature = request.POST['signature']
        signature = signature.encode('utf-8')
        signature = base64.decodestring(signature)

        k = des("414a8023", CBC, "zykzst13", pad=None, padmode=PAD_PKCS5)
        decrypted_key = k.decrypt(signature,padmode=PAD_PKCS5)
        if decrypted_key == feeTime:
            try:
                dialog = Dialog.objects.get(id = dialogID,dialogSession=dialogKey) #todo
                dialog.all_time= allTime
                dialog.charging_time = feeTime
                dialog.state = 4
                dialog.save()
                cloopenAccounts =CloopenAccount.objects.filter(dialogID = dialog.id)
                for ca in cloopenAccounts:
                    ca.state =0
                    ca.save()
                teacher = User.objects.get(id = dialog.teacherId)
                teacher.activeState = 1
                teacher.save()
            except: 
                return HttpResponse('yes')
            try:
                question = Question.objects.get(id = dialog.questionId)
                question.state = 3
                question.save()
            except:
                return HttpResponse('change question state fail')
            return HttpResponse('yes')
        return Httpresponse('invalid signature')

    except:
        return HttpResponse('parament wrong')


def push_call_request_2_teacher(teacherID,question,dialog,userID):
    root = ROOT_PATH
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
    message.setProperty("pushType",10)
    message.setProperty("info",[dialog.id,dialog.dialogSession,question.id,question.title,question.authorRealName,'media'+question.thumbnails,question.description,question.subject])
    message.badge(1)
    message.sound()

    # add message to tuple and send it to APNS server
    wrapper.append(message)
    wrapper.connect()
    wrapper.notify()

def push_call_response_2_student(dialog,cloopen_account,voIPAccount2):
    print '######## push response'
    root = ROOT_PATH
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
    message.setProperty("pushType",20)
    message.setProperty("info",[dialog.id,dialog.dialogSession,cloopen_account.cloudAccount,cloopen_account.cloudSecret,cloopen_account.voIPAccount,cloopen_account.voIPSecret,voIPAccount2])
    message.badge(1)
    message.sound()
    print message.__str__()

    # add message to tuple and send it to APNS server
    wrapper.append(message)
    wrapper.connect()
    wrapper.notify()
def push_call_reject_2_student(dialog):
    print '######## push response'
    root = ROOT_PATH
    wrapper = APNSNotificationWrapper(os.path.join(root,'mobileapp','ck.pem'), True,True,True)
    session = Session.objects.get(userID = dialog.studentId)
    token = session.push_token.replace(' ','')
    token = token.replace('<','')
    token = token.replace('>','')
    deviceToken = binascii.unhexlify(token)
    # create message
    message = APNSNotification()
    message.token(deviceToken)
    message.alert(u'a dialog reject')
    message.setProperty("pushType",21)
    message.badge(1)
    message.sound()
    print message.__str__()

    # add message to tuple and send it to APNS server
    wrapper.append(message)
    wrapper.connect()
    wrapper.notify()


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

def dialog_time(request):
    try:
        username = request.POST['username']
        password = request.POST['password']
    except:
        message = '参数不正确'
        return redirect('/dialog/time')
    try:
        m = hashlib.md5()
        m.update(password)
        psw = m.hexdigest()
        user = User.objects.get(username  = username, password = psw)
        return render(request,'dialog/time.html',locals())
    except:
        message = '用户名或密码不正确'
        return redirect('dialog/time')
   
