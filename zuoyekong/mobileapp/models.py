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

    phone.primary_key = True


class Session(models.Model):
    phone = models.BigIntegerField()
    token = models.CharField(max_length=100)


    def is_session_token_valid(self,phone, token):
        try:
            Session.objects.get(phone=phone, token=token)
            return True
        except Exception:
            return False

    def generate_session_token(self,phone):
        try:
            token = uuid.uuid4().hex
            self.phone = phone
            self.token = token
            self.save()
            return token
        except Exception:
            return False