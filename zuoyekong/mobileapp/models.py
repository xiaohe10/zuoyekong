from django.db import models
from random import Random
import uuid




class User(models.Model):
    phone = models.BigIntegerField()
    password = models.CharField(max_length=100)
    nickname = models.CharField(max_length=100)
    type = models.CharField(max_length=10)
    school = models.CharField(max_length=200)
    grade = models.CharField(max_length=20)
    created_time = models.DateTimeField(auto_now_add=True)
    headImage = models.FileField(upload_to='headImages/%Y/%m/%d')

    def safe_get(self,phone):
        try:
            user = User.objects.get(phone = phone)
            return user
        except Exception:
            return None


class ValildCode(models.Model):
    phone = models.BigIntegerField()
    codeType = models.CharField(max_length=20)
    code = models.CharField(max_length=10)

    def is_code_valid(self,phone,codeType,code):
        try:
            validcode = ValildCode.objects.get(phone = phone, codeType=codeType,code=code)
            validcode.delete()
            return True
        except Exception:
            return False

    def generate_valid_code(self,phone,codeType):
        #todo add createtime then we can limit the gap bewteen two request for valid code
        try:
            try:
                 same_validcodes = ValildCode.objects.filter(phone = phone, codeType=codeType)
                 for validcode in same_validcodes:
                    validcode.delete()
            except Exception:
                print Exception
            self.phone = phone
            self.codeType = codeType
            self.code = '123456'
            self.save()
            return True
        except Exception:
            return False
class Session(models.Model):
    phone = models.BigIntegerField()
    session_ID = models.CharField(max_length=100)
    session_key = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)


    def generate_session_token(self,phone):
        try:
            session_ID = uuid.uuid1().hex
            session_key = uuid.uuid4().hex
            self.session_ID = session_ID
            self.phone = phone
            self.session_key = session_key
            self.save()
            return {"session_ID":session_ID,"session_key":session_key}
        except Exception:
            return False

class Question(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    subject = models.CharField(max_length=20)
    grade = models.CharField(max_length=20)
    author = models.BigIntegerField() # user id

    def get_question_list_by_user(self,user_id):
        question_list = Question.objects.filter(author = user_id)
        final_question_list = []
        for question in question_list:
            final_question = {}
            final_question['ID'] = question.id
            final_question['grade'] = question.grade
            final_question['title'] = question.title
            final_question['subject'] = question.subject
            final_question['description'] = question.description
            image_list = QuestionImages.objects.filter(questionId = question.id)
            final_image_list=[]
            for image in image_list:
                final_image_list.append(image.image)
            final_question['questionImages'] = final_image_list
            final_question_list.append(final_question)
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
            question_detail['author'] = question.author
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
    state = models.CharField(max_length=20) #unread/read/cancel/
    created_time = models.DateTimeField(auto_now_add=True)

class Dialog(models.Model):
    studentId = models.BigIntegerField() #student user id
    tearcherId = models.BigIntegerField() # teacher user id
    questionId = models.BigIntegerField() # question id
    state = models.CharField(max_length=20) #waiting/refused/inDialog/finished
    dialogSession = models.CharField(max_length=100)
    created_time = models.DateTimeField(auto_now_add=True)
    all_time = models.BigIntegerField() # all talk time in secondes
    charging_time  = models.BigIntegerField() # duration that charge