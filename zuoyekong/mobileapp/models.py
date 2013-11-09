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

    phone.primary_key = True

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
    author = models.ForeignKey('User')
class QuestionImages(models.Model):
    questionId = models.ForeignKey(Question)
    image = models.FileField(upload_to='questionPictures/%Y/%m/%d')