# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse
from django.core.cache import cache

from mobileapp.models import *
from django.http import HttpResponseRedirect
import hashlib
import time

from django.shortcuts import render

def is_online(session_ID,session_key):
    key = cache.get(session_ID)
    if(key and key == session_key):
        return True
    else:
        try:
            session = Session.objects.get(session_ID=session_ID,session_key=session_key)
            cache.set(session_ID,session_key,600)
            return True
        except Exception:
            return False
def account_test(request):
    user = None
    try:
        phone = request.GET['phone']
        session_key = request.GET['sessionKey']
        session_ID = request.GET['sessionID']
        if(is_online(session_ID=session_ID,session_key = session_key)):
            user = User()
            user = user.safe_get(phone = phone)
        else:
            user = None
    except Exception:
        user = None
    return render(request,'account/test.html',locals())
    
def send_register_valid_code(request):
    try:
        phone = request.POST['phone']
        try:
            user = User.objects.get(phone=phone)
            return HttpResponse(json.dumps({'result':'fail','errorType':101,'msg':'already registered'}))
        except Exception:
            if(True):
                validcode = ValidCode()
                validcode.generate_valid_code(phone=phone,codeType='REGISTER')
                return HttpResponse(json.dumps({'result':'success'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

def login_do(request):
    try:
        phone = request.POST['phone']
        password = request.POST['password']
        m = hashlib.md5()
        m.update(password)
        psw = m.hexdigest()
        try:
            user = User.objects.get(phone=phone)
            if(user.password != psw):
                return HttpResponse(json.dumps({'result':'fail','errorType':105,'msg':'wrong password'}))
            else:
                session = Session()
                token = session.generate_session_token(phone)
                if (token):
                    cache.set(token['session_ID'],token['session_key'],600)
                    return HttpResponse(json.dumps({'result':'success','sessionID':token['session_ID'],'sessionKey':token['session_key']}))
                else:
                    return HttpResponse(json.dumps({'result':'fail','errorType':501,'msg':'cannot generate token'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','errorType':104,'msg':'no such user'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

def register_do(request):
    try:
        phone = request.POST['phone']
        password = request.POST['password']
        m = hashlib.md5()
        m.update(password)
        psw = m.hexdigest()
        code = request.POST['registerValidCode']
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))
    try:
        type = request.POST['type']
    except Exception:
        type=''
    try:
        school = request.POST['school']
    except Exception:
        school = ''
    validcode = ValidCode()
    if(validcode.is_code_valid(phone = phone,codeType='REGISTER',code=code)):
        try:
            user = User.objects.get(phone=phone)


def logout(request):
    try:
        userName = request.POST['userName']
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        try:
            cache.delete(session_ID)
            session = Session.objects.get(userName=userName,session_ID=session_ID,session_key=session_key)
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
            validcode.generate_valid_code(userName,'FINDPASS')
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
        if(validcode.is_code_valid(userName = userName,codeType='FINDPASS',code=code)):
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
        user = User.objects.get(userName=userName)
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
        userName = request.POST['userName']
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        if(is_online(session_ID = session_ID,session_key=session_key)):
            try:
                user = User.objects.get(userName = userName)
                profile = {}
                profile['userName'] = user.userName
                profile['type'] = user.type
                profile['grade'] = user.grade
                if user.headImage:
                    profile['headImage'] = 'media/'+user.headImage.__str__()
                else:
                    profile['headImage'] = ''
                profile['nickname'] = user.nickname
                return HttpResponse(json.dumps(profile))
            except Exception:
                return HttpResponse(json.dumps({'result':'fail','errorType':102,'msg':'no such user'}))
        else:
            return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))
def modify_profile(request):
    try :
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']

        session = Session()
        userName = session.get_user_userName(session_ID,session_key)
        if not userName:
            return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'invalid session'}))
        try:
            user = User.objects.get(userName = userName)
            if request.POST.has_key('school'):
                user.school = request.POST['school']
            if request.POST.has_key('grade'):
                user.grade = request.POST['grade']
            if request.POST.has_key('nickname'):
                user.nickname = request.POST['nickname']
            if request.FILES.has_key('headImage'):
                user.headImage = request.FILES['headImage']
            user.save()
            return HttpResponse(json.dumps({'result':'success'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','errorType':102,'msg':'no such user'}))

    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':201,'msg':'wrong request params'}))

# This Python file uses the following encoding: utf-8 #author : xiaoh16@gmail.com import json from django.http import HttpResponse from django.core.cache import cache from mobileapp.models import *
from django.http import HttpResponseRedirect
import hashlib
import time

from django.shortcuts import render

