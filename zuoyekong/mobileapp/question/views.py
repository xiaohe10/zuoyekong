# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render
from zuoyekong.settings import SITE_URL
import Image
import os
from zuoyekong.settings import MEDIA_ROOT
from django.db.models.fields.files import FileField
import mobileapp.account.views
from django.http import HttpResponseRedirect
from django.db.models import Q


def verify_access_2_question(sessionID,questionid):
    try:
        session = Session.objects.get(session_ID = sessionID)
        Question.objects.get(authorID = session.userID,id=questionid)
        return True
    except Exception:
        return False

def verify_access_2_add_picture(sessionID,questionid):
    try:
        session = Session.objects.get(session_ID = sessionID)
        Question.objects.get(session.userID,id=questionid)
        return True
    except:
        try:
            Dialog.objects.get(questionID = questionid,teacherId = session.userID,state = 3)
            return  True
        except:
            return False

def question_test(request):
    return render(request, 'app/question/test.html', locals())


def create_question(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        session = Session()
        userID = session.get_userID(session_ID,session_key)
        if not userID:
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 203, 'msg': 'no such session'}))
        try:
            user = User.objects.get(id = userID)
        except Exception:
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 102, 'msg': 'no such user'}))
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
        if request.FILES.has_key('voice'):
            question.voice = request.FILES['voice']
        else:
            question.voice = ''
        question.state = 1
        if request.POST.has_key('state'):
            question.state = request.POST['state']
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
                        ext = os.path.splitext(os.path.basename(questionImage.image.path))[1]
                        try:
                            originfile =  os.path.join(MEDIA_ROOT,questionImage.image.path)
                            image = Image.open(originfile)
                            print Image.ANTIALIAS
                            print image.thumbnail((256,256),Image.ANTIALIAS)
                            origin_dirname = os.path.dirname(originfile)
                            thumb_dirname = origin_dirname.replace('questionPictures','questionThumbnails')
                            thumb_path = os.path.join(thumb_dirname,question.id.__str__()+'_thumb'+ext)
                            if not os.path.exists(thumb_dirname):
                                os.makedirs(thumb_dirname)
                            image.save(thumb_path)
                            thumb_path = thumb_path.encode('utf-8')
                            thumb_path = thumb_path.replace('\\','/')
                            origin_relative_path = thumb_path.replace(MEDIA_ROOT,'')
                            relative_path = origin_relative_path.replace('questionPictures','questionThumbnails')
                            question.thumbnails = relative_path
                            question.save()
                        except Exception:
                            print Exception
        teachers = []
        if request.POST.has_key('teacherNumber'):
            n = int(request.POST['teacherNumber'])
            count = 0
            while(n > 0):
                n = n - 1
                count += 1
                if request.POST.has_key('teacher'+count.__str__()):
                    t = {}
                    try:
                        teacherID = request.POST['teacher'+count.__str__()]
                        teacher = User.objects.filter(id = teacherID).get(userType = 2)
                        #todo push to teacher
                        t['result'] = 'success'
                        t['teacherID'] = teacherID
                    except:
                        t['result'] = 'fail'
                        t['errorType'] = 107
                        t['teacherID'] = teacherID
                        t['msg'] =  'no such teacher'
                    teachers.append(t)
        push_new_question_to_teacher()
        return HttpResponse(json.dumps({'result': 'success','questionID':question.id,'teachers':teachers}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'success','questionID':question.id}))
from mobileapp.APNSWrapper import *
from zuoyekong.settings import ROOT_PATH
import threading
import binascii
import hashlib
def push_to_a_teacher(session):
    try:
        root = ROOT_PATH
        wrapper = APNSNotificationWrapper(os.path.join(root,'mobileapp','ck.pem'), True,False,True)
        token = session.push_token.replace(' ','')
        if token == '':
            return
        token = token.replace('<','')
        token = token.replace('>','')
        deviceToken = binascii.unhexlify(token)
        # create message
        message = APNSNotification()
        message.token(deviceToken)
        message.alert(u'有新的问题发布了！')
        message.setProperty("pushType",32)

        message.badge(1)
        message.sound()
        # add message to tuple and send it to APNS server
        wrapper.append(message)
        wrapper.connect()
        wrapper.notify()
    except:
        print 'push to teacher' + str(session.userID) + 'fail'
def push_new_question_to_teacher():
    sessions = Session.objects.all()
    lock = threading.Lock()
    for session in sessions:
        user = User.objects.get(id = session.userID)
        if user.userType == 2:
            threading.Thread(target=push_to_a_teacher,args=(session,)).start()
def list_history_question(request):
    try:
        print request
        sessionID = request.POST['sessionID']
        print sessionID
        sessionKey = request.POST['sessionKey']
        print sessionKey
        subject = None
        if request.POST.has_key('subject'):
           subject =  request.POST['subject']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
    s = Session()
    userID = s.get_userID(sessionID,sessionKey)
    if User:
        q = Question()
        history_list = q.get_history_list(userID=userID,subject = subject)
        return HttpResponse(json.dumps({'result':'success','questionList':history_list}))
    else:
        return HttpResponse(json.dumps({'result': 'fail','errorType': 203, 'msg': 'no such session'}))
def get_history_detail(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']
        questionID = request.POST['questionID']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
    if mobileapp.account.views.is_online(session_ID=sessionID, session_key=sessionKey):

        if verify_access_2_question(sessionID,questionID):
            q = Question()
            result = {'result':'success'}
            question_detail = q.get_history_detail(questionID)
            if not question_detail:
                return HttpResponse(json.dumps({'result': 'fail','errorType': 301, 'msg': 'question state wrong'}))
            result = dict(result, **question_detail)
            return HttpResponse(json.dumps(result))
        else:
            return HttpResponse(json.dumps({'result': 'fail','errorType': 301, 'msg': 'cannot access question or no question'}))
    else:
        return HttpResponse(json.dumps({'result': 'fail','errorType': 203, 'msg': 'no such session'}))
def list_user_question(request):
    try:
        userID = request.POST['userID']
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        updateTime = None
        questionState = None
        limit = 1000
        offset = 0
        subject = None
        if request.POST.has_key('updateTime'):
            updateTime = None if (request.POST['updateTime'] == '') else request.POST['updateTime']
        if request.POST.has_key('state'):
            questionState = None if (request.POST['state'] == '') else request.POST['state']
        if request.POST.has_key('limit'):
            limit = 1000 if (request.POST['limit'] == '') else request.POST['limit']
        if request.POST.has_key('offset'):
            offset = 0 if (request.POST['offset'] == '') else request.POST['offset']
        if request.POST.has_key('subject'):
            subject = None if (request.POST['subject'] == '') else request.POST['subject']
        if mobileapp.account.views.is_online(session_ID=session_ID, session_key=session_key):
            question = Question()
            question_list = question.get_question_list(sessionId = session_ID,user_id = userID,update_time=updateTime,state = questionState,subject = subject,limit=limit,offset=offset)
            return HttpResponse(json.dumps({'result': 'success', 'questionList':question_list}))
        else:
            return HttpResponse(json.dumps({'result': 'fail','errorType': 203, 'msg': 'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))

def show_question(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_ID = request.POST['questionID']
        if mobileapp.account.views.is_online(session_ID=session_ID, session_key=session_key):
            question = Question()
            question_detail = question.get_question_detail_by_id(question_id=question_ID)
            if(verify_access_2_question(session_ID,question_ID)):
                question.update_application_number(question_ID)
            return HttpResponse(json.dumps({"questiondetail":question_detail,"result":"success"}))
        else:
            return HttpResponse(json.dumps({'result': 'fail','errorType': 203, 'msg': 'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))

def update_question(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        questionID = request.POST['questionID']
        session = Session()
        userID = session.get_userID(session_ID,session_key)
        if not userID:
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 203, 'msg': 'no such session'}))
        if not verify_access_2_question(session_ID,questionID):
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 301, 'msg': 'cannot access to question'}))
        try:
            question = Question.objects.get(id = questionID)
        except:
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 301, 'msg': 'question doesnt exist or has been deleted'}))
        user=User.objects.get(id  = userID)
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
        if request.FILES.has_key('voice'):
            question.voice = request.FILES['voice']
        else:
            question.voice = ''
        question.status = 1
        if request.POST.has_key('state'):
            question.state = request.POST['state']
        question.save()
        applications = Application.objects.filter(questionId = question.id)
        for a in applications:
            a.delete()
            #todo: push to teacher
        if request.POST.has_key('pictureNumber'):
            images = QuestionImages.objects.filter(questionId = question.id)
            for image in images:
                image.delete()
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
                            thumb_path = thumb_path.encode('utf-8')
                            thumb_path = thumb_path.replace('\\','/')
                            origin_relative_path = thumb_path.replace(MEDIA_ROOT,'')
                            relative_path = origin_relative_path.replace('questionPictures','questionThumbnails')
                            question.thumbnails = relative_path
                            question.save()
                        except Exception:
                            print Exception
        teachers = []

        if request.POST.has_key('teacherNumber'):
            n = int(request.POST['teacherNumber'])
            count = 0
            while(n > 0):
                n = n - 1
                count += 1
                if request.POST.has_key('teacher'+count.__str__()):
                    t = {}
                    try:
                        teacherID = request.POST['teacher'+count.__str__()]
                        teacher = User.objects.filter(id = teacherID).get(userType = 2)
                        #todo push to teacher
                        t['result'] = 'success'
                        t['teacherID'] = teacherID
                    except:
                        t['result'] = 'fail'
                        t['errorType'] = 107
                        t['teacherID'] = teacherID
                        t['msg'] =  'no such teacher'
                    teachers.append(t)
        result = {'result': 'success','questionID':question.id, 'teachers': teachers}
        return HttpResponse(json.dumps(result))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))


def delete_question(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_ID = request.POST['questionID']

        if mobileapp.account.views.is_online(session_ID=session_ID, session_key=session_key):
            if verify_access_2_question(session_ID,question_ID):
                q = Question.objects.get(id = question_ID)
                q.delete()
                return HttpResponse(json.dumps({'result':'success','questionID':question_ID}))
            else:
                return HttpResponse(json.dumps({'result': 'fail','errorType': 202, 'msg': 'cannot operate on this question or question doesnt exist'}))
        else:
            return HttpResponse(json.dumps({'result': 'fail', 'errorType': 203,'msg': 'no such session'}))
    except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
def add_image(request):
     try:
        print request
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        question_ID = request.POST['questionID']
        print question_ID
        image = QuestionImages(questionId = question_ID)
        print image
        print image.image
        try:
            image.image = request.FILES['image']
            image.save()
        except:
            return HttpResponse(json.dumps({'result': 'fail','errorType': 202, 'msg': 'store file error'}))
        imageCount = QuestionImages.objects.filter(questionId = question_ID).count() - 1
        print imageCount
        return HttpResponse(json.dumps({'result':'success','imageID':imageCount}))
     except Exception:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
def get_image(request,questionID,imageID):
    try:
        questionID = int(questionID.encode('utf-8'))
        imageID = int(imageID.encode('utf-8'))
        url = QuestionImages.objects.filter(questionId = questionID)[imageID]
        url = url.image.__str__()
        return HttpResponseRedirect('http://'+SITE_URL +'/media/' +url)
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'no such image'}))



def search_question(request):
    try:
        session_ID = request.POST['sessionID']
        session_key = request.POST['sessionKey']
        limit = 10000
        offset = 0
        if request.POST.has_key('limit'):
            limit  = request.POST['limit']
            if not limit:
                limit = 10000
        else:
            limit = 10000 
        if request.POST.has_key('offset'):
            offset  = request.POST['offset']
            if not offset:
                offset = 0
        else:
            offset = 0
        all_questions = Question.objects.filter(state=1).order_by('-updateTime')
        questions = []
        if request.POST.has_key('subject'):
            subjects = request.POST['subject']
            subject_list = subjects.split('|')
            query = None
            for s in subject_list:
                if query:
                    query  = query|Q(subject = s)
                else:
                    query = Q(subject = s)
            all_questions = all_questions.filter(query)
        if request.POST.has_key('grade'):
            grades = request.POST['grade']
            grade_list = grades.split('|')
            query = None
            for g in grade_list:
                if query:
                    query  = query|Q(grade = g)
                else:
                    query = Q(grade = g)
            all_questions = all_questions.filter(query)
        try:
                questions = all_questions[int(offset):int(offset)+int(limit)]
        except:
            try:
                questions = all_questions[int(offset):]
            except:
                questions = []
        question_list = []
        for question in questions:
            final_question = {}
            final_question['ID'] = question.id
            final_question['grade'] = question.grade
            final_question['title'] = question.title
            final_question['subject'] = question.subject
            final_question['description'] = question.description
            final_question['state'] = question.state
            final_question['thumbnails'] = 'media'+question.thumbnails
            final_question['authorID'] = question.authorID
            final_question['authorRealName'] = question.authorRealName
            final_question['unreadApplicationNumber'] = question.unread_applicationNumber
            final_question['applicationNumber'] = question.applicationNumber
            final_question['updateTime'] = question.updateTime.__str__()
            question_list.append(final_question)
        return HttpResponse(json.dumps({'result': 'success', 'questionList': question_list}))
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
