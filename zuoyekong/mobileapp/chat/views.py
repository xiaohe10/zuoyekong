# This Python file uses the following encoding: utf-8
#author : xiaoh16@gmail.com
import json

from django.http import HttpResponse
from zuoyekong.settings import ROOT_PATH
from mobileapp.models import *
from django.core.cache import cache
from django.shortcuts import render
from django.shortcuts import render_to_response
from mobileapp.account.views import is_online
import os
import binascii
from mobileapp.APNSWrapper import *
from django.db.models import Q

def test(request):
    return render_to_response('app/chat/test.html',locals())
def get_contact_list(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
    try:
        userID = Session.objects.get(session_ID = sessionID,session_key = sessionKey).userID
        user = User.objects.get(id = userID)
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'no such session'}))
    query = Q(senderID = userID) | Q(receiverID = userID)
    chats = Chat.objects.filter(query).order_by('-id')
    contact_list = []
    contact_unread_msg_counter = {}
    contact_last_time = {}
    for chat in chats:
        if chat.receiverID != userID:
            anotherID = chat.receiverID
        else:
            anotherID = chat.senderID
        if anotherID not in contact_list:
            contact_list.append(anotherID)
            contact_unread_msg_counter[anotherID] = 0
            contact_last_time[anotherID] = chat.time.__str__()
        if chat.receiverID == userID and chat.state == 'U':
            contact_unread_msg_counter[anotherID] += 1
    contact_detail_list = []
    for contact in contact_list:
        try:
            user = User.objects.get(id = contact)
            contact_detail = {}
            contact_detail['userID'] = contact
            contact_detail['nickname'] = user.realname if user.realname != '' else user.userName
            contact_detail['headURL'] = 'media/'+user.headImage.__str__()
            contact_detail['unReadConter'] = contact_unread_msg_counter[contact]
            contact_detail['lastTime'] = contact_last_time[contact]
            contact_detail_list.append(contact_detail)
        except:
            print 'wrong userId in contact list'
    return HttpResponse(json.dumps({'result':'success','contacts':contact_detail_list}))

def get_unread_msgs(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']
        senderID = request.POST['senderID']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
    try:
        userID = Session.objects.get(session_ID = sessionID,session_key = sessionKey).userID
        user = User.objects.get(id = userID)
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'no such session'}))
    chats = Chat.objects.filter(senderID = senderID,state = 'U').order_by('id')
    messages = []
    for chat in chats:
        chat.state = 'R'
        chat.save()
        msg = {}
        msg['id'] = chat.id
        msg['senderID'] = chat.senderID
        msg['msgTime'] = chat.time.__str__()
        msg['msgContent'] = chat.message
        messages.append(msg)
    return HttpResponse(json.dumps({'result':'success','msgs':messages}))

def get_all_msgs(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']
        senderID = request.POST['senderID']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
    try:
        userID = Session.objects.get(session_ID = sessionID,session_key = sessionKey).userID
        user = User.objects.get(id = userID)
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'no such session'}))
    query = Q(senderID = senderID, receiverID = userID) | Q(receiverID = senderID,senderID = userID)
    chats = Chat.objects.filter(query).order_by('-id')
    if chats.count() > 50:
        chats = chats[0,50]
    chats = chats.reverse()
    messages = []
    for chat in chats:
        if chat.state == 'U':
            chat.state = 'R'
            chat.save()
        msg = {}
        msg['id'] = chat.id
        msg['senderID'] = chat.senderID
        msg['msgTime'] = chat.time.__str__()
        msg['msgContent'] = chat.message
        messages.append(msg)
    return HttpResponse(json.dumps({'result':'success','msgs':messages}))

def send_msg(request):
    try:
        sessionID = request.POST['sessionID']
        sessionKey = request.POST['sessionKey']
        receiverID = request.POST['receiverID']
        msgContent = request.POST['msgContent']
    except:
        return HttpResponse(json.dumps({'result': 'fail', 'errorType': 201, 'msg': 'wrong request params'}))
    try:
        userID = Session.objects.get(session_ID = sessionID,session_key = sessionKey).userID
        user = User.objects.get(id = userID)
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':203,'msg':'no such session'}))
    try:
        receiverID = User.objects.get(id = receiverID).id
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':601,'msg':'no such receive'}))
    try:
        chat = Chat(senderID = userID,receiverID = receiverID,message = msgContent,state = 'U')
        chat.save()
        nickname = user.realname if user.realname != '' else user.userName
        push_msg_thread(nickname,receiverID,msgContent)
        return HttpResponse(json.dumps({'result':'success'}))
    except:
        return HttpResponse(json.dumps({'result':'fail','errorType':000,'msg':'unkown'}))

def push_msg(nickname,receiverID,msgContent):
    try:
        session = Session.objects.get(userID = receiverID)
    except:
        print 'no such session for '+ nickname
        return
    try:
        root = ROOT_PATH
        wrapper = APNSNotificationWrapper(os.path.join(root,'mobileapp','ck.pem'), True,False,True)
        token = session.push_token.replace(' ','')
        if token == '':
            return
        token = token.replace('<','')
        token = token.replace('>','')
        deviceToken = binascii.unhexlify(token)
        # create message
        message = APNSNotification()
        message.token(deviceToken)
        message.alert(u'您有一条新消息')
        message.setProperty("pushType",40)

        message.badge(1)
        message.sound()
        # add message to tuple and send it to APNS server
        wrapper.append(message)
        wrapper.connect()
        wrapper.notify()
    except:
        print 'push message fail'
import threading
def push_msg_thread(nickname,receiverID,msgContent):
    lock = threading.Lock()
    threading.Thread(target=push_msg,args=(nickname,receiverID,msgContent)).start()
