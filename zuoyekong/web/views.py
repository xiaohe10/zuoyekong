# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
from django.shortcuts import render
from django.shortcuts import render_to_response
from django.http import HttpResponseRedirect
# Create your views here.
import hashlib
from mobileapp.models import *
from django.http import HttpResponse
from  django.views.decorators.cache import cache_page
cache_page(120*60)
def home(request):
    if 'username' in request.session:
        username = request.session['username']
    return render_to_response('web/home.html',locals())

def logindo(request):
    try:
        username = request.GET['username']
        password = request.GET['password']
        m = hashlib.md5()
        m.update(password)
        psw = m.hexdigest()
        try:
            user = User.objects.get(userName=username,password = psw)
            request.session['username'] = user.userName
            response = HttpResponseRedirect('/homepage')
            return response
        except:
            message = "用户名或密码错误"
            return render_to_response('app/account/login.html',locals())
    except:
        return HttpResponse('非法的请求')
from time import strftime, strptime
def convert_time(logging_time):
    input_format = "%Y-%m-%d %H:%M:%S+00:00" # or %d/%m...
    output_format = "%Y-%m-%d %H:%M:%S"
    return strftime(output_format, strptime(logging_time, input_format))
from web.alipay import *
def record(request):
    if 'username' in request.session:
        username = request.session['username']
        user = User.objects.get(userName = username)
        all_all_time = 0
        all_charging_time = 0
        all_fee = 0
        if user.userType == 2:
            dialogs = Dialog.objects.filter(teacherId = user.id,all_time__gt = 600000).order_by('-id')

            for dialog in dialogs:
                try:
                    q = Question.objects.get(id = dialog.questionId)
                    dialog.all_time = (dialog.all_time + 60000)/60/1000
                    dialog.charging_time = (dialog.charging_time + 60000)/60/1000
                    dialog.subject = q.get_subject_display()
                    dialog.fee = float(dialog.charging_time) * 5/3
                    dialog.created_time = convert_time( str(dialog.created_time))
                    dialog.other = User.objects.get(id = dialog.studentId).userName
                    dialog.otherName =  User.objects.get(id = dialog.studentId).realname
                    all_all_time += dialog.all_time
                    all_charging_time += dialog.charging_time
                    all_fee += dialog.fee
                except:
                    pass


        else:
            dialogs = Dialog.objects.filter(studentId = user.id,all_time__gt = 600000).order_by('-id')

            for dialog in dialogs:
                try:
                    q = Question.objects.get(id = dialog.questionId)
                    dialog.all_time = (dialog.all_time + 60000)/60/1000
                    dialog.charging_time = (dialog.charging_time + 60000)/60/1000
                    dialog.subject = q.get_subject_display()
                    dialog.fee = dialog.charging_time * 2
                    dialog.created_time = convert_time( str(dialog.created_time))
                    dialog.other = User.objects.get(id = dialog.teacherId).userName
                    dialog.otherName =  User.objects.get(id = dialog.studentId).realname
                    all_all_time += dialog.all_time
                    all_charging_time += dialog.charging_time
                    all_fee += dialog.fee
                except:
                    pass
        return render_to_response('web/record.html',locals())
    else:
        return HttpResponseRedirect('/')

def pay(request):
    try:
        userID = request.POST['userID']
        user = User.objects.get(id = int(userID))
        total_fee = request.POST['total_fee']
        pay = Pay(out_trade_no = uuid.uuid1().hex,userID=userID,total_fee = total_fee,status = 'U')
        pay.save()
        params = {
            'out_trade_no':pay.out_trade_no,
            'subject':'作业控时间',
            'body':'作业控时间详情',
            'total_fee':str(total_fee)}
        alipay = Alipay()
        params.update(alipay.conf)
        sign = alipay.buildSign(params)
        return render_to_response('web/pay.html',locals())
    except:
        return HttpResponse('生成帐单错误')
def pay_callback(request):
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
def homepage(request):
    if 'username' in request.session:
        username = request.session['username']
        user = User.objects.get(userName = username)
        user.headImage = '/media/'+user.headImage.__str__()
        return render(request, 'web/homepage.html',locals())
    else:
        return HttpResponseRedirect('/')
def web_logout(request):
    try:
        del request.session['username']
    except KeyError:
        pass
    return HttpResponseRedirect('/')
cache_page(120*60)
def product(request):
    if 'username' in request.session:
        username = request.session['username']
    return render_to_response('web/product.html',locals())
def team(request):
    return render_to_response('web/team.html',locals())
def contact(request):
    return render_to_response('web/contact.html',locals())
