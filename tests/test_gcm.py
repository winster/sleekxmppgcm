from __future__ import absolute_import
import unittest
import sys
import os
import json
from xml.etree import ElementTree
from binascii import hexlify
from xmppgcm.gcm import GCM, GCMMessage


class TestGCM(unittest.TestCase):

    MSGID = u'm-1366082849205'

    def setUp(self):
        self.was_called_back = False
        self.last_message_id = None
        self.last_from = None
        self.last_message_type = None
        self.last_payload = None

    def test_on_gcm_message_ack(self):
        """ Make GCM instance and inject an ACK, check if:
              - Callback was called.
              - Last message id hangled by GCM match the predefined.
              - Last "from" too.
              - If the ACKS was successfully removed from stack.
        """

        xml = u"""<message id="asdasdas">
                  <gcm xmlns="google:mobile:data">
                  {
                      "from":"aoskdpasdasdasdasd",
                      "message_id":"%s",
                      "message_type":"ack"
                  }
                  </gcm>
              </message>
              """ % (self.MSGID, )
        e = ElementTree.fromstring(xml)

        j = list(e)[0]

        msg = {
            'gcm': GCMMessage(xml=j, parent=None)
        }

        def dummy_callback(a, msgid, data_from):
            self.was_called_back = True
            self.last_message_id = msgid
            self.last_from = data_from

        gcm = GCM('a', 'b')
        gcm.ACKS[self.MSGID] = dummy_callback
        self.assertIn(self.MSGID, gcm.ACKS)
        gcm.on_gcm_message(msg)

        self.assertTrue(self.was_called_back)
        self.assertEquals(self.last_message_id, self.MSGID)
        self.assertEquals(self.last_from, msg['gcm']['from'])
        self.assertNotIn(self.MSGID, gcm.ACKS)

    def test_on_gcm_message_nack(self):
        """ Make GCM instance and inject an NACK, check if:
              - Callback was called.
              - Last message id hangled by GCM match the predefined.
              - Last "from" too.
              - If the ACKS was successfully removed from stack.
        """

        xml = u"""<message>
                  <gcm xmlns="google:mobile:data">
                  {
                    "message_type":"nack",
                    "message_id":"%s",
                    "from":"iasjdoaisjdoaijsiodaisd",
                    "error":"BAD_REGISTRATION",
                    "error_description":"Invalid token"
                  }
                  </gcm>
                </message>
              """ % (self.MSGID, )
        e = ElementTree.fromstring(xml)

        j = list(e)[0]

        msg = {
            'gcm': GCMMessage(xml=j, parent=None)
        }

        def dummy_callback(a, msgid, data_from):
            self.was_called_back = True
            self.last_message_id = msgid
            self.last_from = data_from

        gcm = GCM('a', 'b')
        gcm.ACKS[self.MSGID] = dummy_callback
        self.assertIn(self.MSGID, gcm.ACKS)
        gcm.on_gcm_message(msg)

        self.assertTrue(self.was_called_back)
        self.assertEquals(self.last_message_id, self.MSGID)
        self.assertNotIn(self.MSGID, gcm.ACKS)

    def test_on_gcm_message_connection_draning(self):
        """ Simulate a connection draingin by injecting a
        GCM payload CONNECTION_DRAINING type. It checks:
            - Connection draining to false before inject.
            - Connection draining to true after inject.
        """

        xml = u"""<message>
                      <data:gcm xmlns:data="google:mobile:data">
                      {
                        "message_type":"control",
                        "control_type":"CONNECTION_DRAINING"
                      }
                      </data:gcm>
                  </message>
              """
        j = list(ElementTree.fromstring(xml))[0]

        msg = {
            'gcm': GCMMessage(xml=j, parent=None)
        }

        gcm = GCM('a', 'b')
        self.assertFalse(gcm.connecton_draining)

        gcm.on_gcm_message(msg)

        self.assertTrue(gcm.connecton_draining)

    def test_on_gcm_message_receipt(self):
        # TODO: implement
        pass

    def test_send_gcm(self):
        """ The send_raw function is injected in this
        test, so we can obtain the data that is sent
        from the GCM class, then we parse it an check:
            - Last payload was filled.
            - That parsed payload and JSON contains:
                to, data and message_id
        """

        gcm = GCM('a', 'b')

        def dumm_send_raw(data):
            self.last_payload = data

        def dummy_callback(a, b, c, d):
            pass

        gcm.send_raw = dumm_send_raw

        gcm_to = hexlify(os.urandom(8))
        gcm_data = 'whatever'

        gcm.send_gcm(gcm_to, gcm_data, None, dummy_callback)
        self.assertIsNotNone(self.last_payload)
        e = ElementTree.fromstring(self.last_payload)
        egcm = list(e)[0]
        self.assertEquals(egcm.tag, '{google:mobile:data}gcm')
        json_data = egcm.text
        data = json.loads(json_data)
    
        self.assertIn('to', data)
        self.assertIn('data', data)
        self.assertIn('message_id', data)

        # TODO: assert "data" deeper

    def test_send_gcm_on_connection_draining(self):
        """ Similar to test_send_gcm, but this simulate a
        connection dranining state, so it can be inserted
        in the queue (list) instead of being serialized to
        XML, we check a dict, and no need to parse """

        try:
            from queue import Queue
        except ImportError:
            from Queue import Queue

        q = []

        gcm = GCM('a', 'b')
        gcm.connecton_draining = True
        gcm.QUEUE = q

        def dummy_callback(a, b, c, d):
            pass

        gcm_to = hexlify(os.urandom(8))
        gcm_data = 'whatever'

        self.assertFalse(q)
        gcm.send_gcm(gcm_to, gcm_data, None, dummy_callback)
        self.assertTrue(q)

        payload = q[-1]
    
        self.assertIn('to', payload)
        self.assertIn('data', payload)
        self.assertIn('message_id', payload)

        # TODO: assert "data" deeper

    def test_random_id(self):
        gcm = GCM('a', 'b')
        anid = gcm.random_id()
        self.assertEquals(len(anid), 8)

    def test_connection_draining_property(self):
        gcm = GCM('a', 'b')
        self.assertFalse(gcm.connecton_draining)
        self.assertFalse(gcm.connection_draining)
        gcm.connection_draining = True
        self.assertTrue(gcm.connecton_draining)
        self.assertTrue(gcm.connection_draining)

    def test_compose_raw_message(self):
        gcm = GCM('a', 'b')
        raw_message = gcm.compose_raw_message({
            'to': 'A',
            'message_id': 'ABCD',
            'data': 'Hola mundo </Adios/> <3<',
            'time_to_live': 123124,
            'delivery_receipt_requested': True  
        })
        self.assertTrue(raw_message.startswith('<message'))
        # TODO: improve validation



if __name__ == '__main__':
    unittest.main()