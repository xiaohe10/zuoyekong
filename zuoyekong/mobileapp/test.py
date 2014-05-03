from APNSWrapper import *
import binascii
import os.path
ROOT_PATH = 'f:/github/zuoyekong/zuoyekong'
wrapper = APNSNotificationWrapper(os.path.join(ROOT_PATH, 'mobileapp','ck.pem'))
deviceToken = binascii.unhexlify('0ddbcbe238b92ee5e0ba7e522f84a4098fc0e4e2e8844df118d0d2d53125fdd2')
# create message
message = APNSNotification()
message.token(deviceToken)
message.alert(u"a dialog request")
message.badge(5)
message.sound()
# add message to tuple and send it to APNS server
wrapper.append(message)
wrapper.notify()