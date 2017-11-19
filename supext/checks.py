# -*- coding: utf-8 -*-
import yaml
import time
import sched
import logging
import importlib

class checks():
    def __init__(self, config):
        # Init data
        self.tests = {}
        self.checks = []

        # Get logger
        self.logger = logging.getLogger('supext')
        self.logger.info('Loading checks and test modules')

        # Init scheduler for muted checks
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.scheduler.run()

        # Get checks, add them to self.check and load new test module if needed
        for name, data in config.items():
            # Add it to self.checks and format data
            try:
                check = {
                    'name': name,
                    'test': data.pop('test'),
                    'canary': data.pop('canary', False),
                    'config': data.pop('config', None),
                    'location': data.pop('location', None),
                    'meta': data,
                    'muted': False,
                    'last_result': {}
                }
            except (KeyError):
                self.logger.error('Check {0} is missing a type, ignoring it'.format(name))
                continue

            # Check if the test module isn't already loaded, if it isn't, load it
            # also, add the check to self.checks only if already present or loaded correctly
            # to avoid having checks that tries to call a unloaded test module
            test = check['test']
            if not test in self.tests:
                try:
                    # Get class from module dynamically
                    module = importlib.import_module('supext.modules.tests.{0}'.format(test))
                    self.tests[test] = getattr(module, test)()
                    self.logger.debug('Loaded test {0}'.format(test))
                    self.checks.append(check)
                except (ImportError, AttributeError):
                    self.logger.error('Cannot load test {0}'.format(test))
            else:
                self.checks.append(check)

    def run(self, name, update=True):
        check = self.get(name)
        result = self.tests[check['test']].run(check['config'])
        if update:
            check['last_result'] = result
        return result

    def getCanaries(self):
        canaries = []
        for check in self.checks:
            if check['canary'] == True:
                self.logger.debug('Got canary check {0}'.format(check['name']))
                canaries.append(check)
        return canaries

    def getAll(self):
        return self.checks

    def get(self, name):
        for check in self.checks:
            if check['name'] == name:
                return check
        return None

    def getFromLocation(self, name):
        checks = []
        for check in self.checks:
            if check['location'] == name:
                checks.append(check)
        return checks

    def getMuted(self):
        muted = []
        for check in self.checks:
            if check['muted']:
                muted.append(check)
        return muted

    def mute(self, name, duration=120):
        def unmute(check):
            check['muted'] = False

        check = self.get(name)
        location = self.getFromLocation(name)

        if not check and not location:
            self.logger.warn('Tried to mute unknown check or location {0}'.format(name))
            return False

        # Try to mute the check first
        # Else try location (= mute all checks for location)
        if check:
            check['muted'] = True
            self.scheduler.enter(int(duration), 1, unmute, (check))
        elif location:
            for check in location:
                self.mute(check['name'], duraction)

        return True

