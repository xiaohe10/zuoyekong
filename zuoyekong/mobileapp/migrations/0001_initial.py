# encoding: utf8
from django.db import models, migrations


class Migration(migrations.Migration):
    
    dependencies = []

    operations = [
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('qustionId', models.BigIntegerField(verbose_name=20),), ('applicant', models.BigIntegerField(verbose_name=20),), ('created_time', models.DateTimeField(auto_now_add=True),), ('applicationState', models.IntegerField(default=0, max_length=2),)],
            bases = (models.Model,),
            options = {},
            name = 'Application',
        ),
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('userID', models.BigIntegerField(verbose_name=20),), ('session_ID', models.CharField(max_length=100),), ('session_key', models.CharField(max_length=100),), ('created_time', models.DateTimeField(auto_now_add=True),), ('update_time', models.DateTimeField(auto_now=True),)],
            bases = (models.Model,),
            options = {},
            name = 'Session',
        ),
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('userName', models.CharField(max_length=30),), ('codeType', models.IntegerField(max_length=2),), ('code', models.CharField(max_length=6),), ('createTime', models.DateTimeField(auto_now_add=True),)],
            bases = (models.Model,),
            options = {},
            name = 'ValidCode',
        ),
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('title', models.CharField(max_length=40),), ('description', models.TextField(),), ('subject', models.IntegerField(max_length=2, choices=((1, '\xe8\xaf\xad\xe6\x96\x87',), (2, '\xe6\x95\xb0\xe5\xad\xa6',), (3, '\xe8\x8b\xb1\xe8\xaf\xad',), (4, '\xe7\x89\xa9\xe7\x90\x86',), (5, '\xe5\x8c\x96\xe5\xad\xa6',), (6, '\xe7\x94\x9f\xe7\x89\xa9',), (7, '\xe6\x94\xbf\xe6\xb2\xbb',), (8, '\xe5\x8e\x86\xe5\x8f\xb2',), (9, '\xe5\x9c\xb0\xe7\x90\x86',), (10, '\xe9\x9f\xb3\xe4\xb9\x90',), (11, '\xe7\xbe\x8e\xe6\x9c\xaf',),)),), ('grade', models.IntegerField(max_length=2, choices=((1, '\xe4\xb8\x80\xe5\xb9\xb4\xe7\xba\xa7',), (2, '\xe4\xba\x8c\xe5\xb9\xb4\xe7\xba\xa7',), (3, '\xe4\xb8\x89\xe5\xb9\xb4\xe7\xba\xa7',), (4, '\xe5\x9b\x9b\xe5\xb9\xb4\xe7\xba\xa7',), (5, '\xe4\xba\x94\xe5\xb9\xb4\xe7\xba\xa7',), (6, '\xe5\x85\xad\xe5\xb9\xb4\xe7\xba\xa7',), (7, '\xe5\x88\x9d\xe4\xb8\x80',), (8, '\xe5\x88\x9d\xe4\xba\x8c',), (9, '\xe5\x88\x9d\xe4\xb8\x89',), (10, '\xe9\xab\x98\xe4\xb8\x80',), (11, '\xe9\xab\x98\xe4\xba\x8c',), (12, '\xe9\xab\x98\xe4\xb8\x89',), (13, '\xe5\xa4\xa7\xe4\xb8\x80',), (14, '\xe5\xa4\xa7\xe4\xba\x8c',), (15, '\xe5\xa4\xa7\xe4\xb8\x89',), (16, '\xe5\xa4\xa7\xe5\x9b\x9b',), (16, '\xe7\xa0\x94\xe7\xa9\xb6\xe7\x94\x9f',), (16, '\xe8\x80\x81\xe5\xb8\x88',),)),), ('authorID', models.BigIntegerField(verbose_name=20),), ('authorRealName', models.CharField(max_length=30),), ('state', models.CharField(max_length=10),), ('thumbnails', models.CharField(max_length=100),), ('voice', models.FileField(upload_to='questionVoice/%Y/%m/%d'),), ('updateTime', models.DateTimeField(auto_now=True),), ('applicationNumber', models.IntegerField(default=0),), ('unread_applicationNumber', models.IntegerField(default=0),)],
            bases = (models.Model,),
            options = {},
            name = 'Question',
        ),
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('userName', models.CharField(max_length=30),), ('password', models.CharField(max_length=100),), ('realname', models.CharField(max_length=20),), ('userType', models.IntegerField(max_length=2, choices=((1, '\xe5\xad\xa6\xe7\x94\x9f',), (2, '\xe8\x80\x81\xe5\xb8\x88',), (3, '\xe7\xae\xa1\xe7\x90\x86\xe5\x91\x98',),)),), ('school', models.CharField(max_length=20),), ('grade', models.IntegerField(max_length=5, choices=((1, '\xe4\xb8\x80\xe5\xb9\xb4\xe7\xba\xa7',), (2, '\xe4\xba\x8c\xe5\xb9\xb4\xe7\xba\xa7',), (3, '\xe4\xb8\x89\xe5\xb9\xb4\xe7\xba\xa7',), (4, '\xe5\x9b\x9b\xe5\xb9\xb4\xe7\xba\xa7',), (5, '\xe4\xba\x94\xe5\xb9\xb4\xe7\xba\xa7',), (6, '\xe5\x85\xad\xe5\xb9\xb4\xe7\xba\xa7',), (7, '\xe5\x88\x9d\xe4\xb8\x80',), (8, '\xe5\x88\x9d\xe4\xba\x8c',), (9, '\xe5\x88\x9d\xe4\xb8\x89',), (10, '\xe9\xab\x98\xe4\xb8\x80',), (11, '\xe9\xab\x98\xe4\xba\x8c',), (12, '\xe9\xab\x98\xe4\xb8\x89',), (13, '\xe5\xa4\xa7\xe4\xb8\x80',), (14, '\xe5\xa4\xa7\xe4\xba\x8c',), (15, '\xe5\xa4\xa7\xe4\xb8\x89',), (16, '\xe5\xa4\xa7\xe5\x9b\x9b',), (16, '\xe7\xa0\x94\xe7\xa9\xb6\xe7\x94\x9f',), (16, '\xe8\x80\x81\xe5\xb8\x88',),)),), ('description', models.TextField(),), ('created_time', models.DateTimeField(auto_now_add=True),), ('headImage', models.FileField(upload_to='headImages/%Y/%m/%d'),), ('identify', models.CharField(max_length=10),)],
            bases = (models.Model,),
            options = {},
            name = 'User',
        ),
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('studentId', models.BigIntegerField(verbose_name=20),), ('tearcherId', models.BigIntegerField(verbose_name=20),), ('questionId', models.BigIntegerField(verbose_name=20),), ('state', models.IntegerField(max_length=2, choices=((1, 'WAITING',), (2, 'REFUSED',), (3, 'INDIALOG',), (4, 'FINISHED',),)),), ('dialogSession', models.CharField(max_length=100),), ('created_time', models.DateTimeField(auto_now_add=True),), ('all_time', models.BigIntegerField(),), ('charging_time', models.BigIntegerField(),)],
            bases = (models.Model,),
            options = {},
            name = 'Dialog',
        ),
        migrations.CreateModel(
            fields = [(u'id', models.AutoField(verbose_name=u'ID', serialize=False, auto_created=True, primary_key=True),), ('questionId', models.ForeignKey(to=u'mobileapp.Question', to_field=u'id'),), ('image', models.FileField(upload_to='questionPictures/%Y/%m/%d'),)],
            bases = (models.Model,),
            options = {},
            name = 'QuestionImages',
        ),
    ]
