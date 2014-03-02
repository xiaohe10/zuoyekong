# This Python file uses the following encoding: utf-8
from django.db import models
from random import Random
import uuid
import datetime

GRADE_CHOICES=(
    (1,'一年级'),
    (2,'二年级'),
    (3,'三年级'),
    (4,'四年级'),
    (5,'五年级'),
    (6,'六年级'),
    (7,'初一'),
    (8,'初二'),
    (9,'初三'),
    (10,'高一'),
    (11,'高二'),
    (12,'高三'),
    (13,'大一'),
    (14,'大二'),
    (15,'大三'),
    (16,'大四'),
    (16,'研究生'),
    (16,'老师'),
)
USER_CHOICES=(
    (1,'学生'),
    (2,'老师'),
    (3,'管理员'),
)

VALIDCODE_CHOICES=(
    (1,'注册验证码'),
    (2,'修改密码验证码'),
)
DIALOG_STATE_CHOICES=(
    #waiting/refused/inDialog/finished
    (1,'WAITING'),
    (2,'REFUSED'),
    (3,'INDIALOG'),
    (4,'FINISHED'),
)
SUBJECT_CHOICES=(
    (1,'语文'),
    (2,'数学'),
    (3,'英语'),
    (4,'物理'),
    (5,'化学'),
    (6,'生物'),
    (7,'政治'),
    (8,'历史'),
    (9,'地理'),
    (10,'音乐'),
    (11,'美术'),
)

QUESTION_STATE_CHOICES=(
    (0,'草稿'),
    (1,'尚未解决'),
    (2,'正在解答'),
    (3,'已经解决'),
)
APPLICATION_CHOICES=(
    (1,'未读'),
    (2,'已读')
)
ACTIVE_CHOICES = (
    (1,'在线'),
    (2,'忙碌'),#忙碌表示未活动或者正在讲题
    (3,'离线')
)
CLOOPEN_ACCOUNT_STATE = (
    (0,'空闲'),
    (1,'正在使用')
)
class User(models.Model):
    userName = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    realname = models.CharField(max_length=20)
    userType = models.IntegerField(max_length=2,choices=USER_CHOICES)
    school = models.CharField(max_length=20)
    grade = models.IntegerField(max_length=5,choices=GRADE_CHOICES)
    description = models.TextField()
    created_time = models.DateTimeField(auto_now_add=True)
    headImage = models.FileField(upload_to='headImages/%Y/%m/%d')
    identify = models.CharField(max_length=10,blank = True,)
    evaluation = models.IntegerField(max_length=3,default=0)
    activeState = models.IntegerField(max_length=3,default=3,choices=ACTIVE_CHOICES)
    def safe_get(self,userName):
        try:
            user = User.objects.get(userName = userName)
            return user
        except Exception:
            return None



class ValidCode(models.Model):
    userName = models.CharField(max_length=30)
    codeType = models.IntegerField(max_length=2)
    code = models.CharField(max_length=6)
    createTime = models.DateTimeField(auto_now_add=True)

    def is_code_valid(self,userName,codeType,code):
        try:
            validcode = ValidCode.objects.get(userName = userName, codeType=codeType,code=code)
            validcode.delete()
            return True
        except Exception:
            return False

    def generate_valid_code(self,userName,codeType):
        #todo add createtime then we can limit the gap bewteen two request for valid code
        try:
            try:
                 same_validcodes = ValidCode.objects.filter(userName = userName, codeType=codeType)
                 for validcode in same_validcodes:
                    validcode.delete()
            except Exception:
                print Exception
            self.userName = userName
            self.codeType = codeType
            self.code = '123456'
            self.save()
            return True
        except Exception:
            return False
class Session(models.Model):
    userID = models.BigIntegerField(20)
    session_ID = models.CharField(max_length=100)
    session_key = models.CharField(max_length=100)
    push_token = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


    def generate_session_token(self,userID,push_token):
        try:
            session_ID = uuid.uuid1().hex
            session_key = uuid.uuid4().hex
            self.session_ID = session_ID
            self.userID = userID
            self.session_key = session_key
            self.push_token = push_token
            self.save()
            return {"session_ID":session_ID,"session_key":session_key}
        except Exception:
            return False

    def get_userID(self,session_ID,session_key):
        try:
            session = Session.objects.get(session_ID=session_ID,session_key=session_key)
            return session.userID
        except Exception:
            return  None
def verify_access_2_draft(session_ID,userID):
    try:
        session = Session.objects.get(session_ID = session_ID)
        if int(userID.encode('utf-8')) == session.userID:
            return  True
        return False
    except:
        return False
class Question(models.Model):
    title = models.CharField(max_length=40)
    description = models.TextField()
    subject = models.IntegerField(max_length=2,choices=SUBJECT_CHOICES)
    grade = models.IntegerField(max_length=2,choices=GRADE_CHOICES)
    authorID = models.BigIntegerField(20)
    authorRealName = models.CharField(max_length=30)
    state = models.IntegerField(max_length=2,choices=QUESTION_STATE_CHOICES)
    thumbnails = models.CharField(max_length=100)
    voice = models.FileField(upload_to='questionVoice/%Y/%m/%d')
    updateTime = models.DateTimeField(auto_now_add=True)
    applicationNumber = models.IntegerField(default=0)
    unread_applicationNumber = models.IntegerField(default=0)
    def get_history_detail(self,questionID):
        try:
            q = Question.objects.get(id = questionID,state = 3)
            question = {}
            question['ID'] = q.id
            question['title'] = q.title
            question['description'] = q.description
            question['grade'] = q.grade
            question['subject'] = q.subject
            question['thumbnails']= 'media' + q.thumbnails.__str__()
            question['updateTime'] = q.updateTime.__str__()
            dialog = Dialog.objects.get(questionId = q.id,state = 4)
            dialogDetail = {}
            dialogDetail['dialogID'] = dialog.id
            dialogDetail['teacherID'] = dialog.teacherId
            teacher = User.objects.get(id = dialog.teacherId)
            dialogDetail['teacherName'] = teacher.realname
            dialogDetail['teacherHeadImage'] = teacher.headImage.__str__()
            dialogDetail['createdTime'] = dialog.created_time.__str__()
            question['dialogDetail'] = dialogDetail
            return question
        except:
            return {}
    def  get_history_list(self,userID,subject = None):
        try:
            history_questions = Question.objects.filter(authorID = userID,state = 3)
            if subject:
                history_questions = history_questions.filter(subject = subject)
            historyQuestions = []
            for q in history_questions:
                question = {}
                question['ID'] = q.id
                question['title'] = q.title
                question['description'] = q.description
                question['grade'] = q.grade
                question['subject'] = q.subject
                question['thumbnails']= 'media' + q.thumbnails
                question['updateTime'] = q.updateTime.__str__()
                dialog = Dialog.objects.get(questionId = q.id,state = 4)
                dialogDetail = {}
                dialogDetail['dialogID'] = dialog.id
                dialogDetail['teacherID'] = dialog.teacherId
                dialogDetail['teacherName'] = User.objects.get(id = dialog.teacherId).realname
                dialogDetail['createdTime'] = dialog.created_time.__str__()
                question['dialogDetail'] = dialogDetail
                historyQuestions.append(question)
            return historyQuestions
        except:
            return []
    def get_question_list(self,sessionId,user_id,update_time=None,state=None,subject = None,offset = 0,limit=20):
        if verify_access_2_draft(sessionId,user_id):
            question_list = Question.objects.filter(authorID = user_id).exclude(state = 3).order_by('-updateTime')
        else:
            question_list = Question.objects.filter(authorID = user_id).exclude(state = 3).exclude(state = 0).order_by('-updateTime')
        if update_time:
            t = datetime.datetime.strptime(update_time,'%Y-%m-%d %H:%M:%S')
            question_list = question_list.filter(updateTime__gte = t)
        if subject:
            question_list = question_list.filter(subject = subject)
        try:
            questionList = question_list[int(offset):int(offset)+int(limit)]
        except:
            try:
                questionList = question_list[int(offset):]
            except:
                questionList = []

        final_question_list = []
        for question in questionList:
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
            final_question['updateTime'] = question.updateTime.__str__()
            final_question_list.append(final_question)
        return final_question_list
    def update_application_number(self,questionID):
        try:
            q = Question.objects.get(id = questionID)
            q.unread_applicationNumber = 0
            q.save()
            applications = Application.objects.filter(questionId = questionID)
            for a in applications:
                a.applicationState = 1
                a.save()
        except Exception:
            print 'no such question'
    def get_question_detail_by_id(self,question_id):
        try:
            question = Question.objects.get(id = question_id)
            question_detail = {}
            question_detail['ID'] = question.id
            question_detail['grade'] = question.grade
            question_detail['title'] = question.title
            question_detail['subject'] = question.subject
            question_detail['description'] = question.description
            question_detail['authorID'] = question.authorID
            question_detail['authorRealName'] = question.authorRealName
            question_detail['state'] = question.state
            question_detail['thumbnails'] = 'media'+question.thumbnails
            question_detail['applicationNumber'] = question.applicationNumber
            question_detail['updateTime'] = question.updateTime.__str__()
            if question.voice != '':
                question_detail['voice'] = 'media/'+question.voice.__str__()
            image_list = QuestionImages.objects.filter(questionId = question.id)
            final_image_list=[]
            for image in image_list:
                final_image_list.append('media/'+image.image.__str__())
            question_detail['questionImages'] = final_image_list
            applications = Application.objects.filter(questionId = question_id)
            application_list = []
            for a in applications:
                application = {}
                application['applicationID'] = a.id
                application['applicantID'] = a.applicant
                applicant = User.objects.get(id = a.applicant)
                application['applicantName'] = applicant.realname
                application['evaluation'] = applicant.evaluation
                if applicant.headImage != None:
                    application['applicantHeadImage'] = 'media/'+applicant.headImage.__str__()
                application['school'] = applicant.school
                application['activeState'] = applicant.activeState
                application['createdTime'] = a.created_time.__str__()
                application['state'] = a.applicationState
                application_list.append(application)
            question_detail['applications'] = application_list
            return  question_detail
        except Exception:
            return None
        

class QuestionImages(models.Model):
    questionId = models.BigIntegerField(20)
    image = models.FileField(upload_to='questionPictures/%Y/%m/%d')

class Application(models.Model):
    questionId = models.BigIntegerField(20)
    applicant =  models.BigIntegerField(20)
    created_time = models.DateTimeField(auto_now_add=True)
    applicationState = models.IntegerField(max_length=2,default=0,choices= APPLICATION_CHOICES)

    def list_applications_by_question(self,question_id):
        try:
            query_list = Application.objects.filter(questionId = question_id)
            application_list = []
            for a in query_list:
                application={}
                application['applicationID'] = a.id
                application['applicant']=a.applicant
                application['created_time']=a.created_time.__str__()
                application['question_id']=a.questionId
                try:
                    user = User.objects.get(id=a.applicant)
                    application['applicantName'] = user.realname
                    application['applicantHeadUrl'] = "media/"+user.headImage.__str__()
                    application['evaluation'] = user.evaluation
                    application['school'] = user.school
                    application['grade'] = user.grade
                except:
                    print "no such user"
                application_list.append(application)
            return application_list
        except:
            return None

class Dialog(models.Model):
    studentId =  models.BigIntegerField(20)
    teacherId = models.BigIntegerField(20)
    questionId =models.BigIntegerField(20)
    state = models.IntegerField(max_length=2,choices=DIALOG_STATE_CHOICES)
    dialogSession = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    all_time = models.BigIntegerField() # all talk time in secondes
    charging_time  = models.BigIntegerField() # duration that charge

    def generate_dialog_session(self):
        self.dialogSession = uuid.uuid4().int>>100
class  CloopenAccount(models.Model):
    cloudAccount = models.CharField(max_length=64)
    cloudSecret = models.CharField(max_length=64)
    voIPAccount = models.CharField(max_length=64)
    voIPSecret = models.CharField(max_length=64)
    state = models.IntegerField(choices=CLOOPEN_ACCOUNT_STATE)
    dialogID = models.BigIntegerField(20)

class Follow(models.Model):
    followerId = models.BigIntegerField(20)
    followeeID = models.BigIntegerField(20)
    createdTime = models.DateTimeField(auto_now_add=True)
import json
class PushMessage(models.Model):
    userID = models.BigIntegerField(20)
    pushType = models.IntegerField()
    content = models.TextField()

    def get_message_by_type(self,userID,pushType):
        messages = PushMessage.objects.filter(userID = userID, pushType = pushType)
        r = []
        for m in messages:
            message = {}
            message['pushType'] = m.pushType
            message['content'] = m.content
            m.delete()
            r.append(message)
        return r
    def get_message_by_user(self,userID):
        messages = PushMessage.objects.filter(userID = userID)
        r = []
        for m in messages:
            message = {}
            message['pushType'] = m.pushType
            message['content'] = m.content
            m.delete()
            r.append(message)
        return r
'''
class Comment(models.Model):
    evaluatorID = models.BigIntegerField(20)
    evaluateeID = models.BigIntegerField(20)
'''
