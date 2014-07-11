__author__ = 'xiao'
from mobileapp.models import *
from mobileapp.account.views import is_online
from django.http import HttpResponse
import json
from django.shortcuts import render

def follow_test(request):
    return render(request, 'app/follow/test.html', locals())

def create_follow(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']
        targetUserID = request.POST['targetUserID']
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong paraments'}))
    try:
        session = Session.objects.get(session_ID = sessionID,session_key = sessionKey)
        try:
            Follow.objects.get(followerId = session.userID,followeeID = targetUserID)
            return HttpResponse(json.dumps({'result':'success'}))
        except:
            pass
        follow = Follow(followerId = session.userID,followeeID = targetUserID)
        follow.save()
        return HttpResponse(json.dumps({'result':'success'}))
    except:
        return HttpResponse(json.dumps({'reuslt':'fail','msg':'no such session'}))

def cancle_follow(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']
        targetUserID = request.POST['targetUserID']
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong paraments'}))
    try:
        session = Session.objects.get(session_ID = sessionID,session_key = sessionKey)
    except:
        return HttpResponse(json.dumps({'reuslt':'fail','msg':'no such session'}))
    try:
        follow = Follow.objects.get(followerId = session.userID,followeeID = targetUserID)
        follow.delete()
        return HttpResponse(json.dumps({'result':'success'}))
    except:
        return HttpResponse(json.dumps({'reuslt':'success'}))

def get_followed_teacher(request):
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
