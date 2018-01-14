# -*- coding: utf-8 -*-

import smtplib
import socket
import logging
import time
from jinja2 import Template
from email.mime.text import MIMEText

class email:
    def __init__(self, config):
        # Get logger
        self.logger = logging.getLogger('supext')

        # Init config
        self.host = config['host']
        self.port = config['port']
        self.username = config['username']
        self.password = config['password']
        self.sender = config['from']
        self.groups = config['groups']

    def alert(self, result, check):
        meta = check['meta']
        group = (meta['mail'].get('group', 'default') if meta.get('mail') else 'default')

        if type(group) is list:
            for group_name in group:
                self.sendAlert(check['name'], result, group_name)
        else:
            self.sendAlert(check['name'], result, group)

    def sendAlert(self, name, result, group):
        if group in self.groups:
            self.logger.info('Sending mail to group {0}'.format(group))
            self.sendMail(name, result, group)
        else:
            self.logger.error('Cannot send mail to non-existing group {0}'.format(group))

    def sendMail(self, name, result, group):
        with open(self.groups[group]['content'], 'r') as mail_config_file:
            try:
                body = mail_config_file.read()
            except:
                self.logger.error('Invalid template file')
                return None

        # Create message
        message = MIMEText(Template(body).render(service=name, diagnostic=result['message']))
        message['Subject'] = Template(self.groups[group]['subject']).render(service=name)
        message['From'] = self.sender
        message['To'] = ', '.join(self.groups[group]['address'])

        # Send message
        try:
            smtp = smtplib.SMTP(self.host, self.port)
            smtp.starttls()
            smtp.login(self.username, self.password)
            smtp.sendmail(self.sender, self.groups[group]['address'], message.as_string())
            smtp.quit()
        except Exception as e:
            self.logger.error('Cannot send email for failed check {0}: {1}'.format(name, e))
