from django.conf.urls import patterns, url
from mobileapp.account.views import *
from mobileapp.question.views import *
from mobileapp.application.views import *
from mobileapp.dialog.views import *
from mobileapp.follow.views import *
from mobileapp.recommend.views import *
from zuoyekong import settings
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^media/(?P<path>.*)$', 'django.views.static.serve',{'document_root': settings.MEDIA_ROOT}),
    
    url(r'^uploadFile',upload_file),


    url(r'^account/test',account_test),
    url(r'^account/userNameExist',userName_exist),
    url(r'^account/login/loginDo',login_do),
    url(r'^account/register/registerDo',register_do),
    url(r'^account/register/getValidCode',send_register_valid_code),
    url(r'^account/findPass/getValidCode',send_find_pass_valid_code),
    url(r'^account/findPass/resetPass',reset_pass),
    url(r'^account/modifyPass',modify_pass),
    url(r'^account/logout',logout),
    url(r'^account/profile/modifyProfile',modify_profile),
    url(r'^account/profile/getProfile',get_profile),

    url(r'^question/test',question_test),
    url(r'^question/publishQuestion',create_question),
    url(r'^question/listQuestion',list_user_question),
    url(r'^question/getQuestion',show_question),
    url(r'^question/updateQuestion',update_question),
    url(r'^question/deleteQuestion',delete_question),
    url(r'^question/searchQuestions',search_question),
    url(r'^question/getImage/(\d+)/(\d+)',get_image),
    url(r'^question/addImage',add_image),
    url(r'^question/listHistoryQuestion',list_history_question),
    url(r'^question/historyQuestionDetail',get_history_detail),
    url(r'^recommend/getRecommendTeachers',get_recommended_teacher),
    url(r'^dialog/getRecentTeachers',get_recent_teacher),
    url(r'^follow/getFollowedTeachers',get_followed_teacher),

    url(r'^application/test', application_test),
    url(r'^application/apply',create_application),
    url(r'^application/cancel',cancel_application),
    url(r'^application/listApplications',list_applications),

    url(r'^dialog/test',dialog_test),
    url(r'^dialog/call',create_dialog),
    url(r'^dialog/accept',accept_dialog),
    url(r'^dialog/putCloopenAccount',put_cloopen_account),
    url(r'^dialog/validate',validate),
    url(r'^dialog/commit',commit),
    url(r'^dialog/cancel',cancel_call),
    url(r'^dialog/reject',reject_call),
    
    url(r'^time$',dialog_time),
    url(r'^time/detail$',dialog_time_detail),

    # Examples:
    # url(r'^$', 'zuoyekong.views.home', name='home'),
    # url(r'^zuoyekong/', include('zuoyekong.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
