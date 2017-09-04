# -*- coding: utf-8 -*-

from jinja2 import Template
import sender
from imapclient import IMAPClient
import socket
import logging
import time

class email:

    def __init__(self, config):

        self.logger = logging.getLogger('app_logger')
        self.server = config['host']
        self.port = config['port']
        self.sender = config['sender']
        self.password = config['password']

    def send(self, name, ret, mailto, subject, content, message):

        with open(content, 'r') as mail_config_file:
            try:
                body = mail_config_file.read()
            except:
                self.logger.error('Invalid configuration content file')
                sys.exit(1)

        text_content = Template(body).render(service=name, diagnostic=ret['message'])
        text_subject = Template(subject).render(service=name)

        try:

            test_smtp = sender.Mail(self.server, port=self.port, username=self.sender, password=self.password, use_tls=True)
            test_smtp.send_message(text_subject, to=mailto, fromaddr=self.sender, body=text_content)

        except:

            self.logger.error('Cannot send email {0}'.format(text_subject))
