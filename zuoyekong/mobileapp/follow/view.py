__author__ = 'xiao'
from mobileapp.models import *
from mobileapp.account.views import is_online
from django.http import HttpResponse
import json
def get_recommended_teacher(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_ID = request.POST['questionID']
        if request.POST.has_key('limit'):
            limit  = request.POST['limit']
        else:
            limit = 5
        if request.POST.has_key('offset'):
            offset  = request.POST['offset']
        else:
            offset = 1
        if is_online(session_ID=session_ID, session_key=session_key):
            teachers = User.objects.filter(userType = 2)[offset,offset+limit-1]
            teacher_list = []
            for t in teachers:
                teacher = {}
                teacher['teacherID'] = t.id
                teacher['realname'] = t.realname
                teacher['userType'] = t.userType
                teacher['grade'] = t.grade
                teacher['description'] = t.description
                teacher['headImage'] = t.headImage
                teacher['identify'] = t.identify
                teacher_list.append(teacher)
            return HttpResponse(json.dumps({'result':'success','recommendTeacherList':teacher_list}))
        else:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session'}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'wrong request params'}))