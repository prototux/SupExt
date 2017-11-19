import logging
import importlib

class alerting():
    def __init__(self, global_config):
        self.modules = {}
        self.logger = logging.getLogger('supext')
        self.logger.info('Loading alerting modules')

        for name, config in global_config.items():
            try:
                module = importlib.import_module('supext.modules.alerting.{0}'.format(name))
                self.modules[name] = getattr(module, name)(config)
                self.logger.debug('Loaded alerting module {0}'.format(name))
            except (ImportError, AttributeError):
                self.logger.error('Cannot load alerting module {0}'.format(name))

    def alert(self, result, check):
        for name, module in self.modules.items():
            self.logger.debug('Trying to alert using module {0}'.format(name))
            try:
                module.alert(result, check)
            except Exception as e:
                self.logger.error('Cannot alert using module {0}: {1}'.format(name, e))
