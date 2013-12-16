from django.db import models
from random import Random
import uuid




class User(models.Model):
    userName = models.CharField(max_length=30)
    password = models.CharField(max_length=100)
    realname = models.CharField(max_length=20)
    userType = models.CharField(max_length=10)
    school = models.CharField(max_length=20)
    grade = models.CharField(max_length=5)
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
    codeType = models.CharField(max_length=10)
    code = models.CharField(max_length=6)

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
    userName = models.CharField(max_length=30)
    session_ID = models.CharField(max_length=100)
    session_key = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)


    def generate_session_token(self,userName):
        try:
            session_ID = uuid.uuid1().hex
            session_key = uuid.uuid4().hex
            self.session_ID = session_ID
            self.userName = userName
            self.session_key = session_key
            self.save()
            return {"session_ID":session_ID,"session_key":session_key}
        except Exception:
            return False

    def get_userName(self,session_ID,session_key):
        try:
            session = Session.objects.get(session_ID=session_ID,session_key=session_key)
            return session.userName
        except Exception:
            return  None
class Question(models.Model):
    title = models.CharField(max_length=40)
    description = models.TextField()
    subject = models.CharField(max_length=5)
    grade = models.CharField(max_length=5)
    authorID = models.BigIntegerField() # user id
    authorRealName = models.CharField(max_length=30)
    state = models.CharField(max_length=10)
    thumbnails = models.CharField(max_length=100)
    updateTime = models.DateTimeField(auto_now=True)
     
    def get_question_list(self,user_id,updateTime=None,questionstatus=None,offset = 1,limit=20):
        question_list = Question.objects.filter(authorID = user_id)
        if updateTime:
            question_list = question_list.filter(updateTime >= updateTime)
        if questionstatus:
            question_list = question_list.filter(questionstatus = questionstatus)
        question_list = question_list[offset:offset+limit]
        final_question_list = []
        for question in question_list:
            final_question = {}
            final_question['ID'] = question.id
            final_question['grade'] = question.grade
            final_question['title'] = question.title
            final_question['subject'] = question.subject
            final_question['description'] = question.description
            final_question['state'] = question.state
            final_question['thumbnails'] = question.thumbnails
            final_question['authorID'] = question.authorID
            final_question['authorRealName'] = question.authorRealName
        return final_question_list

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
            question_detail['thumbnails'] = question.thumbnails
            image_list = QuestionImages.objects.filter(questionId = question.id)
            final_image_list=[]
            for image in image_list:
                final_image_list.append(image.image)
            question_detail['questionImages'] = final_image_list
        except Exception:
            return None
        

class QuestionImages(models.Model):
    questionId = models.BigIntegerField() # question id
    image = models.FileField(upload_to='questionPictures/%Y/%m/%d')

class Application(models.Model):
    qustionId = models.BigIntegerField() # question id
    applicant = models.BigIntegerField() # applicant user id
    created_time = models.DateTimeField(auto_now_add=True)

    def list_applications_by_question(self,question_id):
        try:
            query_list = Application.objects.filter(questionId = question_id)
            application_list = []
            for a in query_list:
                application={}
                application['applicant']=a.applicant
                application['created_time']=a.created_time
                application['question_id']=a.qustionId
                application_list.append(application)
        except Exception:
            return None

class Dialog(models.Model):
    studentId = models.BigIntegerField() #student user id
    tearcherId = models.BigIntegerField() # teacher user id
    questionId = models.BigIntegerField() # question id
    state = models.CharField(max_length=20) #waiting/refused/inDialog/finished
    dialogSession = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    all_time = models.BigIntegerField() # all talk time in secondes
    charging_time  = models.BigIntegerField() # duration that charge

    def generate_dialog_session(self):
        return uuid.uuid4().hex
