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

def manage(request):
    dialogs = Dialog.objects.exclude(charging_time = 0)
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
    return render_to_response('manage/../../templates/web/manage/index.html',locals())
import hashlib
def adduser(request):
    if request.POST.has_key('userName'):
        try:
            userName = request.POST['userName']
            try:
                User.objects.get(userName = userName)
                userExists = True
                return render_to_response('manage/../../templates/web/manage/adduser.html',locals())
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
                return render_to_response('manage/../../templates/web/manage/adduser.html',locals())
        except:
            return render_to_response('manage/../../templates/web/manage/adduser.html',locals())

    return render_to_response('manage/../../templates/web/manage/adduser.html',locals())
def userlist(request):
    users = User.objects.all().order_by('userType')
    for user in users:
        user.headImage = '/media/'+user.headImage.__str__()
        user.userType = '老师' if user.userType == 2 else '学生'
        user.grade = user.get_grade_display()
    return render_to_response('manage/../../templates/web/manage/userlist.html',locals())