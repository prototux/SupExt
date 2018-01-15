#!/usr/bin/env python
# -*- coding: utf-8 -*-
import yaml
import sys
import time
import sched
import logging
import logging.handlers
import glob
import threading
import concurrent.futures
from supext import api, checks, connectors, alerting

class supext():
    def __init__(self, config='/etc/supext', noapi=False, debug=False):
        # Set debug and current round
        self.debug = debug
        self.round = None

        # Init logging first
        self.initLogging()

        # Load config files
        self.config = {}
        self.logger.info('Loading configuration')
        self.loadConfig(config)
        if not self.config:
            self.logger.critical('Invalid configuration!')
            sys.exit(1)
        else:
            self.logger.debug('Configuration loaded')

        # Init modules
        self.loadModules()

        # Init API
        if noapi == False and (self.config.get('api') and self.config['api'].get('enabled', True)):
            self.initAPI()

        # Init thread pool for checks
        self.pool = concurrent.futures.ThreadPoolExecutor(max_workers=self.thread_nb)

    def initLogging(self):
        # Create logger with debug level
        self.logger = logging.getLogger('supext')
        self.logger.setLevel(logging.DEBUG)

        # Create the handler and configure it
        handler = logging.handlers.SysLogHandler(address='/dev/log')
        handler.setLevel(logging.ERROR)
        handler.setFormatter(logging.Formatter('supext: %(levelname)s: %(message)s'))

        # Enable log to stderr if we're in debug mode
        if self.debug:
            debugHandler = logging.StreamHandler()
            debugHandler.setLevel(logging.DEBUG)
            debugHandler.setFormatter(logging.Formatter('[%(levelname)s] %(message)s'))
            self.logger.addHandler(debugHandler)

        # Add handler to the logger
        self.logger.addHandler(handler)

    def loadConfig(self, config_path):
        # If we reload, don't reset self.config
        new_config = {}
        configs = ['{0}/config.yml'.format(config_path)]
        configs += glob.glob('{0}/conf.d/*.yml'.format(config_path))

        # TIL: dict.update doesn't merge sub elements...
        def mergeConfig(config, new_config):
            if isinstance(config, dict) and isinstance(new_config, dict):
                for k,v in new_config.items():
                    if k not in config:
                        config[k] = v
                    else:
                        config[k] = mergeConfig(config[k], v)
            elif isinstance(new_config, dict):
                config = new_config
            return config

        # Load config files and merge it into self.config
        for config in configs:
            with open(config, 'r') as config_file:
                try:
                    # Merge this file into the configuration
                    new_config = mergeConfig(new_config, yaml.load(config_file))
                except yaml.YAMLError:
                    self.logger.error('Invalid configuration file {0}'.format(config_file))
                    return None

        # Check if there's checks in config
        if not 'checks' in new_config:
            self.logger.error('No checks in config')
            return None

        # If there's no errors, apply the new configuration
        self.config = new_config

        # Threads
        self.thread_nb = int(self.config.get('threads', 5))

        # Timers (between each round and before retry)
        self.time_rounds = int((self.config.get('timers') or {}).get('rounds', 1200))
        self.time_retry = int((self.config.get('timers') or {}).get('retry', 120))

        # Logging (to a log file, instead of syslog)
        logfile = (self.config.get('logging') or {}).get('file', '/var/log/supext.log')
        level = (self.config.get('logging') or {}).get('level', 'INFO')
        handler = logging.handlers.RotatingFileHandler(logfile, maxBytes=104857600, backupCount=20)
        if hasattr(logging, level):
            handler.setLevel(getattr(logging, level))
        else:
            self.logger.error('Log level {0} doesn\'t exist'.format(level))
            handler.setLevel(logging.INFO)
        handler.setFormatter(logging.Formatter('[%(asctime)s] [%(levelname)s] %(message)s'))
        self.logger.addHandler(handler)

    def loadModules(self):

        # Load checks
        self.checks = checks.checks(self.config['checks'])

        # Load connectors
        if 'connectors' in self.config:
            self.connectors = connectors.connectors(self.config['connectors'])
        else:
            self.connectors = None
            self.logger.warn('No connector found in configuration')

        # Load Alerting modules
        if 'alerting' in self.config:
            self.alerting = alerting.alerting(self.config['alerting'])
        else:
            self.alerting = None
            self.logger.warn('No alerting module found in configuration')

        return None

    def initAPI(self):
        self.api = api.api(self, self.config.get('api'))
        thread = threading.Thread(target=self.api.run)
        thread.daemon = True
        thread.start()

    def runCheck(self, name, alert=False):
        result = self.checks.run(name)
        if self.alerting and not result['ok'] and alert:
            self.logger.error('Check {0} failed for the second time, alerting...'.format(name))
            self.alerting.alert(result, self.checks.get(name))
        elif alert:
            self.logger.info('Check {0} recovered on second try'.format(name))

        # Execute connectors only on success or confirmed fail
        if self.connectors and (result['ok'] or (not result['ok'] and alert)):
            self.connectors.addEntry(result, self.checks.get(name))
        return result

    def runChecks(self):
        # Run canary checks first
        failed_locations = []
        self.logger.info('Running canary checks')
        for check in self.checks.getCanaries():
            result = self.runCheck(check['name'])
            if not result['ok']:
                failed_locations.append(check['location'])
                self.logger.error('Canary check {0} failed'.format(check['name']))
                self.alerting.alert(result, check)
            else:
                self.logger.info('Canary check {0} passed'.format(check['name']))
        self.logger.debug('Canary checks finished, running normal checks (from OK locations)')

        # Run normal checks (in a thread pool)
        results = {}
        for check in self.checks.getAll():
            # Don't queue the check if it's from a failed location or if it's a canary (already done)
            if not check['location'] in failed_locations and not check['canary'] and not check['muted']:
                results[self.pool.submit(self.runCheck, check['name'])] = check['name']
            elif not check['canary'] and not check['muted']:
                self.logger.info('Skipping check {0}, canary check for this location failed'.format(check['name']))
            elif check['muted']:
                self.logger.info('Skipping muted check {0}'.format(check['name']))
        for check in concurrent.futures.as_completed(results):
            name = results[check]
            try:
                result = check.result()

                # Check if result is KO to trigger a double-check in self.time_retry seconds
                if not result['ok']:
                    self.logger.error('Check {0} KO ({1}), retrying in {2} seconds'.format(name, result['message'], self.time_retry))
                    self.scheduler.enter(self.time_retry, 2, self.runCheck, (name, True))
                else:
                    self.logger.info('Check {0} OK ({1})'.format(name, result['message']))
            except Exception:
                self.logger.error('Execution failed for check {0}'.format(name))
                continue
        self.logger.info('Round of checks finished')

    def loop(self):
        self.logger.info('Run new round of checks')
        self.runChecks()
        self.round = self.scheduler.enter(self.time_rounds, 1, self.loop, ())

    def start(self):
        # Load scheduler and enter the matri... loop
        self.scheduler = sched.scheduler(time.time, time.sleep)
        self.scheduler.enter(1, 1, self.loop, ())
        self.scheduler.run()

    def reload(self, signum, frame):
        self.logger.info('Reloading config')
        self.loadConfig()

    def exit(self, signum, frame):
        self.logger.info('Exiting supext')
        sys.exit(0)
