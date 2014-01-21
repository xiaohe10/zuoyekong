# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse
from django.core.cache import cache

from mobileapp.models import *
from django.http import HttpResponseRedirect
import hashlib
import time
from zuoyekong.settings import MEDIA_ROOT
import os
from django.shortcuts import render

def is_online(session_ID,session_key):
    try:
        key = cache.get(session_ID)
        if(key and key == session_key):
            return True
    except:
        print 'cache error'
    try:
        session = Session.objects.get(session_ID=session_ID,session_key=session_key)
        try:
            cache.set(session_ID,session_key,600)
        except:
            print 'cache error'
        return True
    except Exception:
        return False

def account_test(request):
   return render(request,'account/test.html',locals())

def send_register_valid_code(request):
    try:
        userName = request.POST['userName']
        try:
            user = User.objects.get(userName=userName)
            return HttpResponse(json.dumps({'result':'fail','errorType':101,'msg':'already registered'}))
        except Exception:
            validcode = ValidCode()
            if validcode.generate_valid_code(userName=userName,codeType=1):
                return HttpResponse(json.dumps({'result':'success'}))
            else:
                return HttpResponse(json.dumps({'result':'fail','errorType':501,'msg':'mysql error'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

def login_do(request):
    try:
        userName = request.POST['userName']
        password = request.POST['password']
        push_token = ''
        if request.POST.has_key('token'):
            push_token = request.POST['token']
        m = hashlib.md5()
        m.update(password)
        psw = m.hexdigest()
        try:
            user = User.objects.get(userName=userName)
            if(user.password != psw):
                return HttpResponse(json.dumps({'result':'fail','errorType':105,'msg':'wrong password'}))
            else:
                sessions = Session.objects.filter(userID=user.id)
                for s in sessions:
                    try:
                        cache.delete(s.session_ID)
                    except:
                        print 'cache error'
                    s.delete()
                    #todo push alert to client
                session = Session()
                user.activeState = 1
                user.save()
                token = session.generate_session_token(user.id,push_token = push_token)
                if (token):
                    try:
                        cache.set(token['session_ID'],token['session_key'],600)
                    except:
                        print 'cache error'
                    return HttpResponse(json.dumps({'result':'success','userID':user.id,'sessionID':token['session_ID'],'sessionKey':token['session_key'],'type':user.userType}))
                else:
                    return HttpResponse(json.dumps({'result':'fail','errorType':501,'msg':'cannot generate token'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','errorType':104,'msg':'no such user'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

def userName_exist(request):
    try:
        userName = request.POST['userName']
        try:
            user = User.objects.get(userName = userName)
            return HttpResponse(json.dumps({'result':'success','userExist':'yes'}))
        except:
            return HttpResponse(json.dumps({'result':'success','userExist':'no'}))
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

def register_do(request):
    try:
        userName = request.POST['userName']
        password = request.POST['password']
        m = hashlib.md5()
        m.update(password)
        psw = m.hexdigest()
        code = request.POST['registerValidCode']
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))
    userType = 1
    school = ''
    grade = 1
    if request.POST.has_key('type'):
        userType = request.POST['type']
    if request.POST.has_key('school'):
        school = request.POST['school']
    if request.POST.has_key('grade'):
        grade = request.POST['grade']
    validcode = ValidCode()
    print code
    if(validcode.is_code_valid(userName = userName,codeType=1,code=code)):
        try:
            user = User.objects.get(userName=userName)
            return HttpResponse(json.dumps({'result':'fail','errorType':101,'msg':'userName has registered'}))
        except Exception:
            newUser = User()
            newUser.userName = userName
            newUser.password = psw
            newUser.userType = userType
            newUser.school = school
            newUser.grade = grade
            newUser.evaluation = 0
            newUser.save()
            return HttpResponse(json.dumps({'result':'success'}))
    else:
        return HttpResponse(json.dumps({'result':'fail','errorType':103,'msg':'wrong valid code'}))

def logout(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        try:
            session = Session.objects.get(session_ID=session_ID,session_key=session_key)
            cache.delete(session_ID)
            session.delete()
            return HttpResponse(json.dumps({'result':'success'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

def send_find_pass_valid_code(request):
    try:
        userName = request.POST['userName']
        try:
            User.objects.get(userName = userName)
            validcode = ValidCode()
            validcode.generate_valid_code(userName,2)
            return HttpResponse(json.dumps({'result':'success'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','errorType':104,'msg':'no such user'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

def reset_pass(request):
    try:
        userName = request.POST['userName']
        newPass = request.POST['password']
        code = request.POST['findPassValidCode']
        validcode = ValidCode()
        if(validcode.is_code_valid(userName = userName,codeType=2,code=code)):
            user = User.objects.get(userName = userName)
            m = hashlib.md5()
            m.update(newPass)
            psw = m.hexdigest()
            user.password = psw
            user.save()
            return HttpResponse(json.dumps({'result':'success'}))
        else:
            return HttpResponse(json.dumps({'result':'fail','errorType':103,'msg':'wrong valid code'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

def modify_pass(request):
    try:
        userName = request.POST['userName']
        oldPass = request.POST['oldPass']
        newPass = request.POST['newPass']
        m = hashlib.md5()
        m.update(oldPass)
        psw = m.hexdigest()
        try:
            user = User.objects.get(userName=userName)
        except:
            return HttpResponse(json.dumps({'result':'fail','errorType':103,'msg':'no such user'}))
        if(psw == user.password):
            m = hashlib.md5()
            m.update(newPass)
            psw = m.hexdigest()
            user.password = psw
            user.save()
            return HttpResponse(json.dumps({'result':'success'}))
        else:
            return HttpResponse(json.dumps({'result':'fail','errorType':105,'msg':'wrong password'}))

    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))
def get_profile(request):
    try:
        userID = request.POST['userID']
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        if(is_online(session_ID = session_ID,session_key=session_key)):
            try:
                user = User.objects.get(id = userID)
                profile = {}
                profile['userID'] = user.id
                profile['userName'] = user.userName
                profile['userType'] = user.userType
                profile['school']= user.school
                profile['description']= user.description
                profile['grade'] = user.grade
                profile['realname'] = user.realname
                profile['identify'] = user.identify
                if user.headImage:
                    profile['headurl'] = 'media/'+user.headImage.__str__()
                comments = [{'evaluatorID':1,'evaluatorName':'匿名学生','content':'给32个赞','mark':4,'headurl':'media/questionThumbnails/2014/01/12/6_thumb.jpg'},
                            {'evaluatorID':2,'evaluatorName':'匿名学生','content':'给32个赞','mark':5,'headurl':'media/questionThumbnails/2014/01/12/6_thumb.jpg'},
                            {'evaluatorID':3,'evaluatorName':'匿名学生','content':'给32个赞','mark':4,'headurl':'media/questionThumbnails/2014/01/12/6_thumb.jpg'},
                            {'evaluatorID':4,'evaluatorName':'匿名学生','content':'给32个赞','mark':5,'headurl':'media/questionThumbnails/2014/01/12/6_thumb.jpg'},
                            {'evaluatorID':4,'evaluatorName':'匿名学生','content':'给32个赞','mark':5,'headurl':'media/questionThumbnails/2014/01/12/6_thumb.jpg'}]
                profile['comments'] = comments
                return HttpResponse(json.dumps({'profile':profile,'result':'success'}))
            except Exception:
                return HttpResponse(json.dumps({'result':'fail','errorType':104,'msg':'no such user'}))
        else:
            return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))
def modify_profile(request):
    try :
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        session = Session()
        print session_ID
        print session_key
        userID = session.get_userID(session_ID,session_key)
        if not userID:
            return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'invalid session'}))
        try:
            user = User.objects.get(id = userID)
            if request.POST.has_key('school'):
                user.school = request.POST['school']
            if request.POST.has_key('grade'):
                user.grade = request.POST['grade']
            if request.POST.has_key('realname'):
                user.realname = request.POST['realname']
            if request.POST.has_key('description'):
                user.description = request.POST['description']
            if request.FILES.has_key('headurl'):
                user.headurl = request.FILES['headurl']
            user.save()
            return HttpResponse(json.dumps({'result':'success'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','errorType':104,'msg':'no such user'+userID}))

    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))
def upload_file(request):
    try:
        #print request
        file = os.path.join(MEDIA_ROOT,'test/test2.png')
        print request
        if request.POST.has_key('file'):
            binary_file = request.POST['file']
            print binary_file
            f = open(file,'wb')
            f.write(binary_file)
            f.close()
        if request.FILES.has_key('file'):
            f = request.FILES['file']
            destination = open(file, 'wb+')
            for chunk in f.chunks():
                destination.write(chunk)
            destination.close()
        return HttpResponse('upload success')
    except:
        return HttpResponse('upload fail')
