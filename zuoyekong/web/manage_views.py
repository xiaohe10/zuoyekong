# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse
from django.http import HttpResponseRedirect
from zuoyekong.settings import ROOT_PATH
from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render
from django.shortcuts import render_to_response

from mobileapp.account.views import is_online
import os
import binascii
from mobileapp.APNSWrapper import *
from  django.views.decorators.cache import cache_page
from time import strftime, strptime
def convert_time(logging_time):
    input_format = "%Y-%m-%d %H:%M:%S+00:00" # or %d/%m...
    output_format = "%Y-%m-%d %H:%M:%S"
    return strftime(output_format, strptime(logging_time, input_format))
import time
cache_page(15*60)
def manage(request):
    if 'username' in request.session:
        username = request.session['username']
        if username != 'admin':
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/web/login')
    type = 'index'
    start_time = time.strftime( "%Y-%m-%d %H:%M", time.localtime() )
    end_time = time.strftime(  "%Y-%m-%d %H:%M", time.localtime() )
    if request.POST.has_key('state'):
        state = request.POST['state']
        if state == 'finished':
            start_time = request.POST['start_time']
            end_time = request.POST['end_time']
            mintime = int(request.POST['mintime']) #
            dialogs = Dialog.objects.filter(created_time__gte = start_time,created_time__lte = end_time,charging_time__gte = mintime*60*1000,state = 4)
        else:
            dialogs = Dialog.objects.filter(state = 1)
        dialogs = list(dialogs)
        for dialog in dialogs:
            try:
                q = Question.objects.get(id = dialog.questionId)
                teacher = User.objects.get(id = dialog.teacherId)
                student = User.objects.get(id = dialog.studentId)
                dialog.created_time = convert_time( str(dialog.created_time))
                dialog.teacher = teacher.userName
                dialog.teacherName = teacher.realname
                dialog.student = student.userName
                dialog.studentName = student.realname
                dialog.subject = q.get_subject_display()
                dialog.all_time = float(dialog.all_time)/60000
                dialog.charging_time = float(dialog.charging_time)/60000
            except:
                dialogs.remove(dialog)
    return render_to_response('web/manage/index.html',locals())
'''
def manage(request):
    dialogs = Dialog.objects.exclude(charging_time = 0).all()
    for dialog in dialogs:
        q = Question.objects.get(id = dialog.questionId)
        teacher = User.objects.get(id = dialog.teacherId)
        student = User.objects.get(id = dialog.studentId)
        dialog.teacher = teacher.userName
        dialog.teacherName = teacher.realname
        dialog.student = student.userName
        dialog.studentName = student.realname
        dialog.subject = q.get_subject_display()
        dialog.all_time = float(dialog.all_time)/60000
        dialog.charging_time = float(dialog.charging_time)/60000
    return render_to_response('web/manage/index.html',locals())
    '''
import hashlib
def adduser(request):
    type = 'adduser'
    if 'username' in request.session:
        username = request.session['username']
        if username != 'admin':
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/web/login')
    if request.POST.has_key('userName'):
        try:
            userName = request.POST['userName']
            try:
                User.objects.get(userName = userName)
                userExists = True
                return render_to_response('web/manage/adduser.html',locals())
            except:
                user = User()
                user.userName = userName
                password = request.POST['password']
                m = hashlib.md5()
                m.update(password)
                psw = m.hexdigest()
                user.password = psw
                user.userType = request.POST['userType']
                user.grade = request.POST['grade']
                user.school = request.POST['school']
                user.description = request.POST['description']
                user.realname = request.POST['realname']
                user.hometown = request.POST['hometown']
                user.highschool = request.POST['highschool']
                user.gender = request.POST['gender']
                user.good_at = request.POST['good_at']
                user.birth = request.POST['birth']

                if request.FILES.has_key('headImage'):
                    user.headImage = request.FILES['headImage']
                user.save()
                addSuccess = True
                return render_to_response('web/manage/adduser.html',locals())
        except:
            return render_to_response('web/manage/adduser.html',locals())

    return render_to_response('web/manage/adduser.html',locals())
def userlist(request):
    type = 'userlist'
    if 'username' in request.session:
        username = request.session['username']
        if username != 'admin':
            return HttpResponseRedirect('/')
    else:
        return HttpResponseRedirect('/web/login')
    users = User.objects.all().order_by('userType')
    for user in users:
        user.headImage = '/media/'+user.headImage.__str__()
        user.userType = '老师' if user.userType == 2 else '学生'
        user.grade = user.get_grade_display()
    return render_to_response('web/manage/userlist.html',locals())