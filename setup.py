from os.path import join, dirname
from setuptools import setup

setup(
  name = 'xmppgcm',
  packages = ['xmppgcm'], # this must be the same as the name above
  version = '0.2.4',
  description = 'Client Library for Firebase Cloud Messaging using XMPP',
  long_description = open(join(dirname(__file__), 'README.txt')).read(),
  install_requires=['sleekxmpp',],
  author = 'Winster Jose',
  author_email = 'wtjose@gmail.com',
  url = 'https://github.com/winster/xmppgcm',
  keywords = ['gcm', 'fcm', 'xmpp', 'xmppgcm', 'xmppfcm'], # arbitrary keywords
  classifiers = [],
)
