# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render

from mobileapp.account.views import is_online
from mobileapp.question.views import verify_access_2_question


def dialog_test(request):
    return render(request, 'dialog/test.html')

def create_dialog(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        application_id = request.POST['applicationID']
        question_id = request.POST['questionID']
        s = Session()
        phone  = s.get_user_phone(session_ID=session_ID,session_key=session_key)
        if not phone:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session'}))
        try:
            student = User.objects.get(phone=phone)
        except Exception:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such user'}))
        try:
            application = Application.objects.get(id=application_id,questionId=question_id)
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','msg':'no such application'}))
        if not verify_access_2_question(sessionID=session_ID,questionid=question_id):
            return HttpResponse(json.dumps({'result':'fail','msg':'cannot access to question'}))
        dialog = Dialog()
        dialog.studentId = student.id
        dialog.tearcherId = application.applicant
        dialog.dialogSession = dialog.generate_dialog_session()
        dialog.state = 'waiting'
        dialog.save()
        return HttpResponse(json.dumps({'result': 'success','dialogID':dialog.id,'dialogSession':dialog.dialogSession}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'wrong request params'}))

def cancel_call(request):
    return True
def verify_dialog_session(request):
    return True

def reject_call(request):
    return True

def answer_call(request):
    return True
def stop_dialog(request):
    return True


def push_call_request_2_teacher():
    return True

def push_call_response_2_student():
    return True

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

