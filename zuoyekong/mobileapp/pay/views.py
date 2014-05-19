# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse

from mobileapp.models import *
from web.alipay import *
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
from django.shortcuts import render_to_response

def app_pay_number(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']

    except:
        return HttpResponse('参数错误')
        #return render_to_response('app/pay/pay_number.html',locals())
    try:
        session = Session.objects.get(session_ID  = sessionID,session_key = sessionKey)
        userID = session.userID
        user = User.objects.get(id = userID)
    except:
        return HttpResponse('权限错误')
        #return render_to_response('app/pay/pay_number.html',locals())
    return render_to_response('app/pay/pay_number.html',locals())
def app_pay_order(request):
    try:
        userID = request.POST['userID']
        total_fee = request.POST['total_fee']
    except:
        return HttpResponse('参数错误')
    try:
        user = User.objects.get(id = userID)
    except:
        return HttpResponse('权限错误')
    try:

        pay = Pay(out_trade_no = uuid.uuid1().hex,userID=userID,total_fee = total_fee,status = 'U')
        pay.save()
        params = {
            'out_trade_no':pay.out_trade_no,
            'subject':'作业控时间',
            'body':'作业控时间详情',
            'total_fee':str(total_fee)}
        alipay = Alipay(notifyurl="http://zuoyekong.com/app_pay/pay_callback",
                 returnurl="http://zuoyekong.com/app_pay/pay_show",
                 showurl="http://zuoyekong.com/app_pay/pay_show")
        params.update(alipay.conf)
        sign = alipay.buildSign(params)
        return render_to_response('app/pay/pay_order.html',locals())
    except:
        return HttpResponse('生成帐单错误')
def app_pay_show(request):
    return render_to_response('app/pay/pay_show.html',locals())
def app_pay_callback(request):
    params = request.POST.dict()
    alipay = Alipay()
    sign=None
    if params.has_key('sign'):
        sign=params['sign']
    locSign=alipay.buildSign(params)

    if sign==None or locSign!=sign:
        print "sign error."
        return HttpResponse("fail")

    if params['trade_status']!='TRADE_FINISHED' and  params['trade_status']!='TRADE_SUCCESS':
        return HttpResponse("fail")

    else:
        print "Verify the request is call by alipay.com...."
        url = verfyURL['http'] + "&partner=%s&notify_id=%s"%(alipay.conf['partner'],params['notify_id'])
        response=urllib2.urlopen(url)
        html=response.read()

        print "aliypay.com return: %s" % html
        if html=='true':
            try:
                out_trade_no = params['out_trade_no']
                trade_no = params['trade_no']
                buyer_id = params['buyer_id']
                buyer_email = params['buyer_email']
                total_fee = params['total_fee']
                pay = Pay.objects.get(out_trade_no = out_trade_no)
                if pay.status == 'S':
                    return HttpResponse("success")
                pay.status = 'S'
                pay.trade_no = trade_no
                pay.buyer_id = buyer_id
                pay.buyer_email = buyer_email
                pay.total_fee = total_fee
                pay.save()
                user = User.objects.get(id = pay.userID)
                user.money += float(total_fee)
                user.save()
            except:
                pass
            return HttpResponse("success")

        return HttpResponse("fail")
