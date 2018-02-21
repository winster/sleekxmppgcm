# xmppgcm

xmppgcm is Python (2.x/3.x) client for Firebase/Google Cloud Messaging (FCM/GCM) using the XMPP protocol. This library supports both upstream and downstream messaging. Currently, the scope is limited to sending messages with device registration tokens and topics. [Topic conditions or device groups] are not supported.

### Before you start
  - [Firebase Cloud Messaging with XMPP]
  - [SleekXMPP]


### Events

This library is event-based, similar to Javascript.

All supported events are available in XMPPEvent class:

* XMPPEvent.CONNECTED - Triggered when session is opened
* XMPPEvent.DISCONNECTED - Triggered when connection is closed
* XMPPEvent.RECEIPT - Triggered when a delivery receipt is received from FCM/GCM
* XMPPEvent.MESSAGE - Tiggered when an upstream message is received from another device via FCM/GCM

### Send Message to FCM/GCM server
```sh
xmpp.send_gcm('device_registration_token', data, options, onAcknowledge)
```
`options` is a dictionary where you can supply [options supported by GCM]

### Installation

pip install xmppgcm

### Sample code

```sh
import logging
from xmppgcm import GCM, XMPPEvent

def onAcknowledge(error, message):
    message_id = message.data['message_id']
    message_from = message.data['from']
	if error != None:
		print('Server did not acknowledge message: ID - {0} : from - {1}'.format(message_id, message_from))
	print('Server acknowledged message: ID - {0} : from - {1}'.format(message_id, message_from))
	

def onDisconnect(draining):
	print('inside onDisconnect')
	xmpp.connect(('gcm-preprod.googleapis.com', 5236), use_ssl=True)


def onSessionStart(queue_length):
	print('inside onSessionStart {0}'.format(queue_length))
	data = {'key1': 'value1'}
	options = { 'delivery_receipt_requested': True }
	xmpp.send_gcm('your_device_token', data, options, onAcknowledge)


def onReceipt(data):
	print('inside onReceipt {0}'.format(data))


def onMessage(data):
	print('inside onSessionStart {0}'.format(data))


# optionally, set up logging
logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
logging.debug("Starting up")

xmpp = GCM('your_sender_id@gcm.googleapis.com', 'fcm_server_key')
xmpp.add_event_handler(XMPPEvent.CONNECTED, onSessionStart)
xmpp.add_event_handler(XMPPEvent.DISCONNECTED, onDisconnect)
xmpp.add_event_handler(XMPPEvent.RECEIPT, onReceipt)
xmpp.add_event_handler(XMPPEvent.MESSAGE, onMessage)
xmpp.connect(('fcm-xmpp.googleapis.com', 5236), use_ssl=True) # test environment
# xmpp.connect(('fcm-xmpp.googleapis.com', 5235), use_ssl=True)  # production environment
xmpp.process(block=True)
    
```

### Todos

 - Write Tests
 - Topic Conditions
 - Device groups

License
----

Apache License 2.0


**Free Software, Hell Yeah!**

[//]: # (These are reference links used in the body of this note and get stripped out when the markdown processor does its job. There is no need to format nicely because it shouldn't be seen. Thanks SO - http://stackoverflow.com/questions/4823468/store-comments-in-markdown-syntax)


   [Firebase Cloud Messaging with XMPP]: <https://firebase.google.com/docs/cloud-messaging/server#implementing-the-xmpp-connection-server-protocol>
   [SleekXMPP]: <http://sleekxmpp.com/getting_started/echobot.html>
   [Topic conditions or device groups]: <https://firebase.google.com/docs/cloud-messaging/send-message>
   [options supported by GCM]: <https://firebase.google.com/docs/cloud-messaging/xmpp-server-ref>
