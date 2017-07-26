#!/usr/bin/env python
# -*- coding: utf-8 -*-

import yaml
import sys
import time
import sched
import logging
from logging.handlers import RotatingFileHandler
import importlib
import argparse
import signal
from daemon import runner
from modules import cachet
from modules import email
from modules import es

class App():
    def __init__(self):
        self.logger = logging.getLogger('app_logger')
        self.logger.setLevel(logging.DEBUG)
        ch = RotatingFileHandler('/var/log/supext/supext.log', maxBytes=1024 * 1024 * 100, backupCount=20)
        ch.setLevel(logging.DEBUG)
        formatter = logging.Formatter("[%(asctime)s] [%(levelname)s] %(message)s")
        ch.setFormatter(formatter)
        self.logger.addHandler(ch)


    def loadTests(self):
        self.tests = {}
        for name, data in self.config['tests'].items():
            if not data['type'] in self.tests:
                try:
                    # Get class from module dynamically
                    test = getattr(importlib.import_module('tests.{0}'.format(data['type'])), data['type'])
                    self.tests[data['type']] = test()
                    self.logger.info('Loaded test {0}'.format(data['type']))
                except ImportError:
                    self.logger.error('Cannot load test {0}'.format(data['type']))

    def loadConfig(self):
        with open("/etc/supext/config.yml", 'r') as config_file:
            try:
                self.config = yaml.load(config_file)
            except yaml.YAMLError:
                self.logger.error('Invalid configuration file')
                sys.exit(1)

        # Check if there's actually tests in config.yml
        if not 'tests' in self.config:
            self.logger.error('No tests in config.yml')
            sys.exit(1)

        #instanciate mail, cachet and ES
        self.email = email.email(self.config['email'])
        self.cachet = cachet.cachet(self.config['cachet'])
        self.elasticsearch = es.elasticsearch()

        #instanciate timers
        self.time_between_each_test = int(self.config['timer'].get('time_between_each_test', 300))
        self.time_before_retry = int(self.config['timer'].get('time_before_retry', 60))

    def callTest(self, name, params, retry=False):
        if params['type'] not in self.tests:
            return None

        self.logger.info('=> Running test {0}'.format(name))

        ret = self.tests[params['type']].test(params.get('config'))
        if ret['ok']:
            self.logger.info('Test {0} successful: {1}'.format(name, ret['message']))
            self.logger.info('Updating component {0} on cachet website.'.format(params['component']))
            self.cachet.update(params['component'], ret)
            self.logger.info('Updating data about {0} on elasticsearch database.'.format(params['component']))
            self.elasticsearch.index(name, params['component'], ret, params.get('location'))
        else:
            self.logger.error('Test {0} failed: {1}'.format(name, ret['message']))

        # Double check still failling -> sending email
        if not ret['ok'] and retry:
            self.logger.info('Updating component {0} on cachet website.'.format(params['component']))
            self.cachet.update(params['component'], ret)
            self.logger.info('Updating data about {0} on elasticsearch database.'.format(params['component']))
            self.elasticsearch.index(name, params['component'], ret, params.get('location'))
            if hasattr(self.tests[params['type']], 'email'):
                self.logger.info('Mailing test {0} with it own message.'.format(name))
                message = self.tests[params['type']].email(name, ret, params.get('config'))
            else:
                self.logger.info('Mailing test {0} with standard message.'.format(name))
                message='none'
            if not 'group' in params:
               self.email.send(name, ret, self.config['email']['groups']['default']['address'], self.config['email']['groups']['default']['subject'], self.config['email']['groups']['default']['content'], message)
            else:
               for data in self.config['email']['groups']:
                   if data == params['group']:
                       self.email.send(name, ret, self.config['email']['groups'][data]['address'], self.config['email']['groups'][data]['subject'], self.config['email']['groups'][data]['content'], message)

        return ret['ok']

    def callAllTests(self):
        self.logger.info('---->New iteration of tests')

        for name, params in self.config['tests'].items():
            if not self.callTest(name, params):
                self.scheduler.enter(self.time_before_retry, 2, self.callTest, (name, params, True))
        self.scheduler.enter(self.time_between_each_test, 1, self.callAllTests, ())

    def run(self):
        # Load configuration file
        self.loadConfig()

        # Load scheduler
        self.scheduler = sched.scheduler(time.time, time.sleep)

        # Load tests
        self.loadTests()

        # Enter the matri... the loop
        self.scheduler.enter(1, 1, self.callAllTests, ())
        self.scheduler.run()

    def reload(self, signum, frame):
        self.logger.info('Reloading config')
        self.loadConfig()


app = App()
signal.signal(signal.SIGHUP, app.reload)
app.run()
