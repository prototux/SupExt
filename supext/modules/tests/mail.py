# -*- coding: utf-8 -*-
import smtplib
from email.mime.text import MIMEText
from imaplib import IMAP4
import socket
import logging
import time

class mail:
    def __init__(self):
        socket.setdefaulttimeout(10)

    def run(self, config):
        ret = { 'ok': False, 'message': '' }

        # Define content (subject and body)
        content = 'TEST-{0}'.format(time.time())

        # Create the message to send
        message = MIMEText(content)
        message['Subject'] = content
        message['From'] = config['smtp']['user']
        message['To'] = config['smtp']['to']

        # Try to send the mail
        try:
            smtp = smtplib.SMTP(config['smtp']['host'], config['smtp']['port'])
            smtp.starttls()
            smtp.login(config['smtp']['user'], config['smtp']['pass'])
            smtp.sendmail(config['smtp']['from'], [config['smtp']['to']], message.as_string())
            smtp.quit()
        except:
            ret['ok'] = None
            ret['message'] = 'Cannot send email'
            return ret

        time.sleep(config.get('wait', 10))

        try:
            # Connect and fetch messages
            imap = IMAP4(config['imap']['host'])
            imap.starttls()
            imap.login(config['imap']['user'], config['imap']['pass'])
            imap.select('INBOX')
            typ, data = imap.search(None, 'SUBJECT "{0}"'.format(content))

            # Check if there's any message matching
            if data[0].split():
                ret['ok'] = True
                ret['message'] = 'OK'
            else:
                ret['ok'] = False
                ret['message'] = 'Email not received'

            # Delete messages and logout
            for mail in data[0].split():
                imap.store(mail, '+FLAGS', '\\Deleted')
            imap.expunge()
            imap.close()
            imap.logout()
        except:
            ret['ok'] = True
            ret['message'] = 'Cannot connect to IMAP'
        return ret
