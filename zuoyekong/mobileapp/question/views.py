# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render
import Image
import os
from zuoyekong.settings import MEDIA_ROOT
from django.db.models.fields.files import FileField
import mobileapp.account.views

def verify_access_2_question(sessionID,questionid):
    try:
        session = Session.objects.get(session_ID = sessionID)
        userID = User.objects.get(userName=session.userName).id
        Question.objects.get(author = userID,id=questionid)
        return True
    except Exception:
        return False



def question_test(request):
    question_list = None
    try:
        userName = request.GET['userName']
        session_key = request.GET['sessionKey']
        session_ID = request.GET['sessionID']
        if mobileapp.account.views.is_online(session_ID=session_ID, session_key=session_key):
            question = Question()
            user = User.objects.get(userName=userName)
            question_list = question.get_question_list_by_user(user.id)
        else:
            question_list = None
    except Exception:
        question_list = None
    return render(request, 'question/test.html', locals())


def create_question(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        session = Session()
        userName = session.get_userName(session_ID,session_key)
        if not userName:
            return HttpRepsonse(json.dumps({'result': 'fail', 'errorType': 203, 'msg': 'no such session'}))
        try:
            print '##########'
            user = User.objects.get(userName = userName)
            print user
            print '#####'
        except Exception:
            return HttpReponse(json.dumps({'result': 'fail', 'errorType': 102, 'msg': 'no such user'}))
        question = Question()
        question.authorID = user.id
        question.authorRealName=user.realname
        if request.POST.has_key('title'):
            question.title = request.POST['title']
        if request.POST.has_key('description'):
            question.description = request.POST['description']
        if request.POST.has_key('subject'):
            question.subject = request.POST['subject']
        if request.POST.has_key('grade'):
            question.grade = request.POST['grade']
        question.status = 'unsolved'
        question.save()
        if request.POST.has_key('pictureNumber'):
            n = int(request.POST['pictureNumber'])
            count = 0
            while(n > 0):
                n = n - 1
                count =  count + 1
                if request.FILES.has_key('questionImage'+count.__str__()):
                    questionImage = QuestionImages()
                    questionImage.questionId = question.id
                    questionImage.image = request.FILES['questionImage'+count.__str__()]
                    questionImage.save()
                    if(count == 1):
                        file = request.FILES['questionImage'+count.__str__()]
                        ext = os.path.splitext(os.path.basename(questionImage.image.path))[1]
                        try:
                            originfile =  os.path.join(MEDIA_ROOT,questionImage.image.path)
                            image = Image.open(originfile)
                            image.thumbnail((256,256),Image.ANTIALIAS)
                            origin_dirname = os.path.dirname(originfile)
                            thumb_dirname = origin_dirname.replace('questionPictures','questionThumbnails')
                            thumb_path = os.path.join(thumb_dirname,question.id.__str__()+'_thumb'+ext)
                            if not os.path.exists(thumb_dirname):
                                os.makedirs(thumb_dirname)
                            image.save(thumb_path)
                            origin_relative_path = thumb_path.replace(MEDIA_ROOT+'/','')
                            relative_path = origin_relative_path.replace('questionPictures','questionThumbnails')
                            question.thumbnails = relative_path
                            question.save()
                        except Exception:
                            print Exception

        return HttpResponse(json.dumps({'result': 'success','questionID':question.id}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))



def list_user_question(request):
    try:
        userName = request.POST['userName']
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        print session_key
        if mobileapp.account.views.is_online(session_ID=session_ID, session_key=session_key):
            question = Question()
            user = User.objects.get(userName=userName)
            question_list = question.get_question_list_by_user(user.id)
            return HttpResponse(json.dumps({'result': 'success', 'questionList':question_list}))
        else:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'wrong request params'}))

def show_question(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_ID = request.POST['questionID']
        if mobileapp.account.views.is_online(session_ID=session_ID, session_key=session_key):
            question = Question()
            question_detail = question.get_question_detail_by_id(question_ID=question_ID)
            return HttpResponse(json.dumps({'result': 'success', 'questiondetail':question_detail}))
        else:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'wrong request params'}))

def update_question(request):
    return True

def add_question_picture(request):
    return True

def drop_question_picture(request):
    return True

def delete_question(request):
    try:
        print request
        session_ID = request.POST['sessionID']
        print session_ID
        session_key = request.POST['sessionKey']
        print session_key
        question_ID = request.POST['questionID']
        print question_ID

        if mobileapp.account.views.is_online(session_ID=session_ID, session_key=session_key):
            if verify_access_2_question(session_ID,question_ID):
                try:
                    q = Question.objects.get(id=question_ID)
                    q.delete()
                    return HttpResponse(json.dumps({'result':'success','questionID':question_ID}))
                except Exception:
                    return HttpResponse(json.dumps({'result': 'fail', 'msg': 'question doesnt exist'}))
            else:
                return HttpResponse(json.dumps({'result': 'fail', 'msg': 'cannot access to this question or question not exist'}))
        else:
            return HttpResponse(json.dumps({'result': 'fail', 'msg': 'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 500, 'msg': 'wrong request params'}))
