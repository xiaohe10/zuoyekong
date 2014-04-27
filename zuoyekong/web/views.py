# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
# Create your views here.
import hashlib
from mobileapp.models import *
from django.http import HttpResponse
from  django.views.decorators.cache import cache_page
cache_page(120*60)
def home(request):
    if 'username' in request.session:
        username = request.session['username']
    return render_to_response('web/home.html',locals())

def logindo(request):
    try:
        username = request.GET['username']
        password = request.GET['password']
        m = hashlib.md5()
        m.update(password)
        psw = m.hexdigest()
        try:
            user = User.objects.get(userName=username,password = psw)
            request.session['username'] = user.userName
            response = HttpResponseRedirect('/homepage')
            return response
        except:
            message = "用户名或密码错误"
            return render_to_response('account/login.html',locals())
    except:
        return HttpResponse('非法的请求')
from time import strftime, strptime
def convert_time(logging_time):
    input_format = "%Y-%m-%d %H:%M:%S+00:00" # or %d/%m...
    output_format = "%Y-%m-%d %H:%M:%S"
    return strftime(output_format, strptime(logging_time, input_format))

@cache_page(60*15)
def record(request):
    if 'username' in request.session:
        username = request.session['username']
        user = User.objects.get(userName = username)
        all_all_time = 0
        all_charging_time = 0
        all_fee = 0
        if user.userType == 2:
            dialogs = Dialog.objects.filter(teacherId = user.id,all_time__gt = 600000).order_by('-id')

            for dialog in dialogs:
                try:
                    q = Question.objects.get(id = dialog.questionId)
                    dialog.all_time = (dialog.all_time + 60000)/60/1000
                    dialog.charging_time = (dialog.charging_time + 60000)/60/1000
                    dialog.subject = q.get_subject_display()
                    dialog.fee = float(dialog.charging_time) * 5/3
                    dialog.created_time = convert_time( str(dialog.created_time))
                    dialog.other = User.objects.get(id = dialog.studentId).userName
                    dialog.otherName =  User.objects.get(id = dialog.studentId).realname
                    all_all_time += dialog.all_time
                    all_charging_time += dialog.charging_time
                    all_fee += dialog.fee
                except:
                    pass


        else:
            dialogs = Dialog.objects.filter(studentId = user.id,all_time__gt = 600000).order_by('-id')

            for dialog in dialogs:
                try:
                    q = Question.objects.get(id = dialog.questionId)
                    dialog.all_time = (dialog.all_time + 60000)/60/1000
                    dialog.charging_time = (dialog.charging_time + 60000)/60/1000
                    dialog.subject = q.get_subject_display()
                    dialog.fee = dialog.charging_time * 2
                    dialog.created_time = convert_time( str(dialog.created_time))
                    dialog.other = User.objects.get(id = dialog.teacherId).userName
                    dialog.otherName =  User.objects.get(id = dialog.studentId).realname
                    all_all_time += dialog.all_time
                    all_charging_time += dialog.charging_time
                    all_fee += dialog.fee
                except:
                    pass

        return render_to_response('web/record.html',locals())
    else:
        return HttpResponseRedirect('/')
def homepage(request):
    if 'username' in request.session:
        username = request.session['username']
        user = User.objects.get(userName = username)
        user.headImage = '/media/'+user.headImage.__str__()
        return render(request, 'web/homepage.html',locals())
    else:
        return HttpResponseRedirect('/')
def web_logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return HttpResponseRedirect('/')
cache_page(120*60)
def product(request):
    if 'username' in request.session:
        username = request.session['username']
    return render_to_response('web/product.html',locals())
def team(request):
    return render_to_response('web/team.html',locals())
def contact(request):
    return render_to_response('web/contact.html',locals())