from APNSWrapper import *
import os
import binascii
def push():
    root = '/root/zuoyekong/zuoyekong'
    wrapper = APNSNotificationWrapper(os.path.join(root,'mobileapp','ck.pem'), True,True,True)
    push_token =  '<db089a62 1c440ce6 bb2855d8 a5493b13 587cf51b 3a600cc1 90ff66a3 c821b744>'
    token = push_token.replace(' ','')
    token = token.replace('<','')
    token = token.replace('>','')
    deviceToken = binascii.unhexlify(token)
    # create message
    message = APNSNotification()
    message.token(deviceToken)
    message.alert(u'a dialog request')
    message.setProperty("pushType",31)
    message.badge(1)
    message.sound()

    # add message to tuple and send it to APNS server
    wrapper.append(message)
    wrapper.connect()
    wrapper.notify()
push()
