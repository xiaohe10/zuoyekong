from django.conf.urls import patterns, url

from mobileapp.account.views import *
from mobileapp.question.views import *
# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    url(r'^account/test',account_test),

    url(r'^account/login/loginDo',login_do),
    url(r'^account/register/registerDo',register_do),
    url(r'^account/register/getValidCode',send_register_valid_code),
    url(r'^account/findPass/getValidCode',send_find_pass_valid_code),
    url(r'^account/findPass/resetPass',reset_pass),
    url(r'^account/modifyPass',modify_pass),
    url(r'^account/logout',logout),
    url(r'^account/profile/modifyProfile',modify_profile),

    url(r'^question/createQuestion',create_question)
    # Examples:
    # url(r'^$', 'zuoyekong.views.home', name='home'),
    # url(r'^zuoyekong/', include('zuoyekong.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # url(r'^admin/', include(admin.site.urls)),
)
