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
    return render_to_response('manage/index.html',locals())
def adduser(request):
    if request.POST.has_key('userName'):
        try:
            user = User()
            user.userName = request.POST['userName']
            user.userName = request.POST['password']
            user.userName = request.POST['userType']
            user.userName = request.POST['grade']
            user.userName = request.POST['school']
            user.userName = request.POST['description']
            if request.FILES.has_key('headImage'):
                user.userName = request.FILES['headImage']
        except:
            return render_to_response('manage/adduser.html',locals())

    return render_to_response('manage/adduser.html',locals())