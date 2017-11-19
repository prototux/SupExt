import yaml
import sys
import time
import sched
import logging
import importlib
import argparse
import signal

class connectors():
    def __init__(self, global_config):
        self.modules = {}
        self.logger = logging.getLogger('supext')
        self.logger.info('Loading connector modules')

        # Loading connectors
        for name, config in global_config.items():
            try:
                module = importlib.import_module('supext.modules.connectors.{0}'.format(name))
                self.modules[name] = getattr(module, name)(config)
                self.logger.debug('Loaded connector {0}'.format(name))
            except (ImportError, AttributeError):
                self.logger.error('Cannot load connector {0}'.format(name))

    def addEntry(self, result, check):
        for name, module in self.modules.items():
            self.logger.debug('Add entry using {0} for check {1}'.format(name, check['name']))
            try:
                module.run(result, check)
            except Exception as e:
                self.logger.error('Cannot add entry using {0} for check {1}: {2}'.format(name, check['name'], e))
