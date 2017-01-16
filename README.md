# xmppgcm

xmppgcm is python client for Google (Firebase) Cloud Messaging using XMPP protocol. At the time of writing this, there is no similar library available in pypi repository. Technically this library supports both upstream and downstream messages. But I have not verified upstream messages. Currently the scope is limited to sending messages with device token and topic. [Topic conditions or device groups] are not supported. If anyone is interested to contribute kindly send pull request.

### Before you start
  - [Check GCM XMPP]
  - [SleekXMPP]

> This library uses event based mechanism similar to what JavaScript does

### Events

All supported events are available in XMPPEvent class:

* XMPPEvent.CONNECTED - event when session is started
* XMPPEvent.DISCONNECTED - event when connection is closed
* XMPPEvent.RECEIPT - called if you have requested for message receipt while sending message
* XMPPEvent.MESSAGE - called when an upstream message received from GCM XMPP server (I have not tested this feature)

### Send Message to GCM server
```sh
xmpp.send_gcm('your_device_token', data, options, onAcknowledge)
```
Options is a dictionary where you can give [GCM supported options]

### Installation

pip install xmppgcm

### Sample code

```sh
from xmppgcm import GCM, XMPPEvent

def onAcknowledge(error, message_id, _from):
	if error != None:
		print('not acknowledged by GCM')
	print('id - {0} : from - {1}'.format(message_id, _from))

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

logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
logging.debug("Starting up")

xmpp = GCM('your_project_id@gcm.googleapis.com', 'gcm_api_key')
xmpp.add_event_handler(XMPPEvent.CONNECTED, onSessionStart)
xmpp.add_event_handler(XMPPEvent.DISCONNECTED, onDisconnect)
xmpp.add_event_handler(XMPPEvent.RECEIPT, onReceipt)
xmpp.add_event_handler(XMPPEvent.MESSAGE, onMessage)

xmpp.connect(('gcm-preprod.googleapis.com', 5236), use_ssl=True) #test environment
# xmpp.connect(('gcm-xmpp.googleapis.com', 5235), use_ssl=True)  #prod environment

while True:
    xmpp.process(block=True)

if __name__ == '__main__':
	_pass
```

For library logging put following in your code
```sh
logging.basicConfig(level=logging.DEBUG, format='%(levelname)-8s %(message)s')
logging.debug("Starting up")

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


   [Check GCM XMPP]: <https://firebase.google.com/docs/cloud-messaging/server#implementing-the-xmpp-connection-server-protocol>
   [SleekXMPP]: <http://sleekxmpp.com/getting_started/echobot.html>
   [Topic conditions or device groups]: <https://firebase.google.com/docs/cloud-messaging/send-message>
   [GCM supported options]: <https://firebase.google.com/docs/cloud-messaging/xmpp-server-ref>