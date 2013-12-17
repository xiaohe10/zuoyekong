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
    (1,'尚未解决'),
    (2,'正在解答'),
    (3,'已经解决'),
)
APPLICATION_CHOICES=(
    (1,'未读'),
    (2,'已读')
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
    identify = models.CharField(max_length=10)
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
    created_time = models.DateTimeField(auto_now_add=True)
    update_time = models.DateTimeField(auto_now=True)


    def generate_session_token(self,userID):
        try:
            session_ID = uuid.uuid1().hex
            session_key = uuid.uuid4().hex
            self.session_ID = session_ID
            self.userID = userID
            self.session_key = session_key
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
    updateTime = models.DateTimeField(auto_now=True)
    applicationNumber = models.IntegerField(default=0)
    unread_applicationNumber = models.IntegerField(default=0)

    def get_question_list(self,user_id,update_time=None,state=None,offset = 0,limit=20):
        question_list = Question.objects.filter(authorID = user_id)
        if update_time:
            t = datetime.datetime.strptime(update_time,'%Y-%m-%d %H:%M:%S')
            question_list = question_list.filter(updateTime__gte = t)
        if state:
            question_list = question_list.filter(state = state)
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
            final_question['thumbnails'] = '/media/'+question.thumbnails
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
            applications = Application.objects.filter(qustionId = questionID)
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
            question_detail['thumbnails'] = '/media/'+question.thumbnails
            question_detail['applicationNumber'] = question.applicationNumber
            question_detail['updateTime'] = question.updateTime.__str__()
            question_detail['voice'] = '/media/'+question.voice.__str__()
            image_list = QuestionImages.objects.filter(questionId = question.id)
            final_image_list=[]
            for image in image_list:
                final_image_list.append('/media/'+image.image.__str__())
            question_detail['questionImages'] = final_image_list
            applications = Application.objects.filter(questionId = question_id)
            application_list = []
            for a in applications:
                application = {}
                application['applicantID'] = a.applicant
                application['createdTime'] = a.created_time
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
                application['applicant']=a.applicant
                application['created_time']=a.created_time
                application['question_id']=a.questionId
                application_list.append(application)
        except Exception:
            return None

class Dialog(models.Model):
    studentId =  models.BigIntegerField(20)
    tearcherId = models.BigIntegerField(20)
    questionId =models.BigIntegerField(20)
    state = models.IntegerField(max_length=2,choices=DIALOG_STATE_CHOICES)
    dialogSession = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    all_time = models.BigIntegerField() # all talk time in secondes
    charging_time  = models.BigIntegerField() # duration that charge

    def generate_dialog_session(self):
        return uuid.uuid4().hex

class Follow(models.Model):
    followerId = models.BigIntegerField(20)
    followeeID = models.BigIntegerField(20)
    createdTime = models.DateTimeField(auto_now_add=True)