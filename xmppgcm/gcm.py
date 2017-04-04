import logging
from sleekxmpp.xmlstream.stanzabase import ElementBase
from sleekxmpp import ClientXMPP
from sleekxmpp.stanza import Message
from sleekxmpp.xmlstream import register_stanza_plugin
from sleekxmpp.xmlstream.handler import Callback
from sleekxmpp.xmlstream.matcher import StanzaPath
import uuid,json,random,string


class GCMMessageType(object):
    ACK = 'ack'
    NACK = 'nack'
    CONTROL = 'control'
    RECEIPT = 'receipt'


class XMPPEvent(object):
    CONNECTED = 'client_connected'
    DISCONNECTED = 'client_disconnected'
    ERROR = 'client_error'
    RECEIPT = 'client_receipt'
    MESSAGE = 'client_message'
    ACK = 'ack'
    NACK = 'nack'


class GCMMessage(ElementBase):
    name = 'gcm'
    namespace = 'google:mobile:data'
    plugin_attrib = 'gcm'
    interfaces = set('json_data')
    sub_interfaces = interfaces
    data = {}

    def __init__(self, xml, parent):
        ElementBase.__init__(self, xml, parent)
        json_str = xml.text
        self.data = json.loads(json_str)

    @property
    def is_error(self):
        if 'error' in list(self.data.keys()):
            return True
        return False

    @property
    def error_description(self):
        if 'error_description' in list(self.data.keys()):
            if self.data.get('error_description') != '':
                return ' %s: %s' % (self.data.get('error', ''), self.data.get('error_description', ''))
            else:
                return self.data.get('error')
        return ''

    @property
    def message_id(self):
        return self.data.get('message_id', '')

    @property
    def message_type(self):
        return self.data.get('message_type', '')

    @property
    def control_type(self):
        return self.data.get('control_type', '')


class GCM(ClientXMPP):

    def __init__(self, id, password):
        ClientXMPP.__init__(self, id, password, sasl_mech='PLAIN')
        self.auto_reconnect = True
        self.connecton_draining = False
        self.MSG = '<message><gcm xmlns="google:mobile:data">{0}</gcm></message>'
        self.QUEUE = []
        self.ACKS = {}

        register_stanza_plugin(Message, GCMMessage)

        self.register_handler(
            Callback('GCM Message', StanzaPath('message/gcm'), self.on_gcm_message)
        )

        self.add_event_handler('session_start', self.session_start)
        self.add_event_handler('disconnected', self.on_disconnected)

    def on_gcm_message(self, msg):
        logging.debug('inside on_gcm_message {0}'.format(msg))
        data = msg['gcm']
        logging.debug('Msg: {0}'.format(data))
        if data.message_type == GCMMessageType.NACK:
            logging.debug('Received NACK for message_id: %s with error, %s' % (data.message_id, data.error_description))
            if data.message_id in self.ACKS:
                self.ACKS[data.message_id](data.error_description, data.message_id, data['from'])
                del self.ACKS[data.message_id]

        elif data.message_type == GCMMessageType.ACK:
            logging.debug('Received ACK for message_id: %s' % data.message_id)
            if data.message_id in self.ACKS:
                self.ACKS[data.message_id](None, data.message_id, data['from'])
                del self.ACKS[data.message_id]

        elif data.message_type == GCMMessageType.CONTROL:
            logging.debug('Received Control: %s' % data.control_type)
            if data.control_type == 'CONNECTION_DRAINING':
                self.connecton_draining = True

        elif data.message_type == GCMMessageType.RECEIPT:
            logging.debug('Received Receipts for message_id: %s' % data.message_id)
            self.event(XMPPEvent.RECEIPT, data)

        else:
            if data['from']:
                self.send_gcm({
                                to: data['from'],
                                message_id: data.message_id,
                                message_type: 'ack'
                            })
            self.event(XMPPEvent.MESSAGE, data)

    def session_start(self, event):
        logging.debug("session started")

        if self.connecton_draining == True:
            self.connecton_draining = False
            for i in reversed(self.QUEUE):
                self.send_gcm(i)
            self.QUEUE = []

        self.event(XMPPEvent.CONNECTED, len(self.QUEUE))

    def on_disconnected(self, event):
        logging.debug("Disconnected")
        self.event(XMPPEvent.DISCONNECTED, self.connecton_draining)

    def send_gcm(self, to, data, options, cb):
        message_id = self.random_id()
        payload = {
            'to': to,
            'message_id': message_id,
            'data': data
        }

        if options:
            for key, value in list(options.items()):
                payload[key]= value

        if cb:
            self.ACKS[message_id] = cb

        if self.connecton_draining == True:
            self.QUEUE.append(payload)
        else:
            self.send_raw(self.MSG.format(json.dumps(payload)))

    def random_id(self):
        rid = ''
        for x in range(8): rid += random.choice(string.ascii_letters + string.digits)
        return rid
