# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
import hashlib
def send_register_valid_code(request):
    return HttpResponse(json.dumps({'result':'success'}))

def login_do(request):
    try:
        phone = request.GET['phone']
        password = request.GET['password']
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
        phone = request.GET['phone']
        password = request.GET['password']
        m = hashlib.md5()
        m.update(password)
        code = request.GET['code']
    except Exception:
        return HttpResponse(json.dumps({'result':'fail','msg':'wrong request params'}))
    try:
        type = request.GET['type']
    except Exception:
        type=''
    try:
        school = request.GET['school']
    except Exception:
        school = ''
    psw = m.hexdigest()
    if (code == "123456"):
        try:
            user = User.objects.get(phone=phone,type=type,school=school)
            return HttpResponse(json.dumps({'result':'fail','msg':'already registered'}))
        except Exception:
            newUser = User(phone=phone,password=psw)
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