# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
import hashlib

from django.shortcuts import render
def account_test(request):
    return render(request,'account/test.html',locals())
    
def send_register_valid_code(request):
    try:
        phone = request.GET['phone']
        try:
            user = User.objects.get(phone=phone)
            return HttpResponse(json.dumps({'result':'fail','errorType':501,'msg':'already registered'}))
        except Exception:
            if(True):
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
                    return HttpResponse(json.dumps({'result':'success','token':token}))
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
    psw = m.hexdigest()
    if (code == "123456"):
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
        token = request.GET['sessionToken']
        try:
            session = Session.objects.get(phone=phone,token=token)
            session.delete()
            return HttpResponse(json.dumps({'result':'success'}))
        except Exception:
            return HttpResponse(json.dumps({'result':'fail','msg':'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))

def send_find_pass_valid_code(request):
    try:
        phone = request.GET['phone']
        return HttpResponse(json.dumps({'result':'success'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))

def reset_pass(request):
    try:
        phone = request.POST['phone']
        newPass = request.POST['password']
        code = request.POST['findPassValidCode']
        if(code == '123456')
            user = User(phone = phone)
         
        return HttpResponse(json.dumps({'result':'success'}))
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))