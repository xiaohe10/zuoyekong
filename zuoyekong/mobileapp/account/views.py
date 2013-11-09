# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse
from django.core.cache import cache

from mobileapp.models import *
import hashlib
import time

from django.shortcuts import render
def _is_online(phone,session_ID,session_key):
    key = cache.get(session_ID)
    if(key and key == session_key):
        return True
    else:
        try:
            session = Session.objects.get(phone=phone, session_ID=session_ID,session_key=session_key)
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
        if(_is_online(phone = phone,session_ID=session_ID,session_key = session_key)):
            user = User()
            user = user.safe_get(phone = phone)
        else:
            user = None
    except Exception:
        user = None
    return render(request,'account/test.html',locals())
    
def send_register_valid_code(request):
    try:
        phone = request.GET['phone']
        try:
            user = User.objects.get(phone=phone)
            return HttpResponse(json.dumps({'result':'fail','errorType':501,'msg':'already registered'}))
        except Exception:
            if(True):
                validcode = ValildCode()
                validcode.generate_valid_code(phone=phone,codeType='REGISTER')
                return HttpResponse(json.dumps({'result':'success'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','errorType':500,'msg':'wrong request params'}))

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
                return HttpResponse(json.dumps({'result':'fail','msg':'wrong password'}))
            else:
                session = Session()
                token = session.generate_session_token(phone)
                if (token):
                    cache.set(token['session_ID'],token['session_key'],600)
                    return HttpResponse(json.dumps({'result':'success','sessionID':token['session_ID'],'sessionKey':token['session_key']}))
                else:
                    return HttpResponse(json.dumps({'result':'fail','msg':'cannot get token'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','msg':'no such user'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))

def register_do(request):
    try:
        phone = request.POST['phone']
        password = request.POST['password']
        m = hashlib.md5()
        m.update(password)
        psw = m.hexdigest()
        code = request.POST['registerValidCode']
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))
    try:
        type = request.POST['type']
    except Exception:
        type=''
    try:
        school = request.POST['school']
    except Exception:
        school = ''
    validcode = ValildCode()
    if(validcode.is_code_valid(phone = phone,codeType='REGISTER',code=code)):
        try:
            user = User.objects.get(phone=phone)
            return HttpResponse(json.dumps({'result':'fail','msg':'already registered'}))
        except Exception:
            newUser = User(phone=phone,password=psw,type=type,school=school)
            newUser.save()
            return HttpResponse(json.dumps({'result':'success'}))
    else:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong valid code'}))


def logout(request):
    try:
        phone = request.GET['phone']
        session_ID = request.GET['sessionID']
        session_key = request.GET['sessionKey']
        try:
            cache.delete(session_ID)
            session = Session.objects.get(phone=phone,session_ID=session_ID,session_key=session_key)
            session.delete()
            return HttpResponse(json.dumps({'result':'success'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','msg':'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))

def send_find_pass_valid_code(request):
    try:
        phone = request.GET['phone']
        try:
            User.objects.get(phone = phone)
            validcode = ValildCode()
            validcode.generate_valid_code(phone,'FINDPASS')
            return HttpResponse(json.dumps({'result':'success'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','msg':'no such user'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))

def reset_pass(request):
    try:
        phone = request.POST['phone']
        newPass = request.POST['password']
        code = request.POST['findPassValidCode']
        validcode = ValildCode()
        if(validcode.is_code_valid(phone = phone,codeType='FINDPASS',code=code)):
            user = User.objects.get(phone = phone)
            m = hashlib.md5()
            m.update(newPass)
            psw = m.hexdigest()
            user.password = psw
            user.save()
            return HttpResponse(json.dumps({'result':'success'}))
        else:
            return HttpResponse(json.dumps({'result':'fail','msg':'wrong valid code'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))

def modify_pass(request):
    try:
        phone = request.POST['phone']
        oldPass = request.POST['oldPass']
        newPass = request.POST['newPass']
        m = hashlib.md5()
        m.update(oldPass)
        psw = m.hexdigest()
        user = User.objects.get(phone=phone)
        if(psw == user.password):
            m = hashlib.md5()
            m.update(newPass)
            psw = m.hexdigest()
            user.password = psw
            user.save()
            return HttpResponse(json.dumps({'result':'success'}))
        else:
            return HttpResponse(json.dumps({'result':'fail','msg':'wrong password'}))

    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))

def modify_profile(request):
    try :
        phone = request.POST['phone']
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        if(_is_online(phone = phone,session_ID = session_ID,session_key=session_key)):
            try:
                user = User.objects.get(phone = phone)
                if request.POST.has_key('school'):
                    user.school = request.POST['school']
                if request.POST.has_key('grade'):
                    user.grade = request.POST['grade']
                if request.POST.has_key('nickname'):
                    user.nickname = request.POST['nickname']
                if request.FILES.has_key('headImage'):
                    print "###########headimage##################"
                    print request.FILES['headImage']
                    user.headImage = request.FILES['headImage']
                user.save()
                return HttpResponse(json.dumps({'result':'success'}))
            except Exception:
                return HttpResponse(json.dumps({'result':'fail','msg':'no such user'}))
        else:
            return HttpResponse(json.dumps({'result':'fail','msg':'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))

