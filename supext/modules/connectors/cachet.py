import sys
import requests
import logging

class cachet:
    def __init__(self, config):
        self.url = config['url']
        self.token = config['token']
        self.logger = logging.getLogger('supext')
        self.certificate = None
        self.key = None
        if config.get('certificate') and config.get('key'):
            self.certificate = config['certificate']
            self.key = config['key']

    def getHeader(self):
        return {'X-Cachet-Token': self.token}

    def getCert(self):
        if self.key and self.certificate:
            return (self.certificate, self.key)
        return None

    def getComponent(self, name):
        try:
            req = requests.request("GET", '{0}/components?name={1}'.format(self.url, name), headers=self.getHeader(), cert=self.getCert())
        except:
            self.logger.error("Cachet component {0} doesn't exist".format(name))
            return None

        raw = req.json()
        if 'data' in raw:
            return raw['data'][0]['id'], raw['data'][0]['status']
        else:
            self.logger.error('Cachet returned an invalid response for component {0}'.format(name))

        return None

    def run(self, result, check):
        # Get name of component
        name = (check['meta']['cachet'].get('component') if check['meta'].get('cachet') else None)
        if not name:
            self.logger.warn('Check {0} doesn\'t have a cachet component, skipping'.format(check['name']))
            return None

        # Get status from result
        if result['ok'] == True:
            status = '1'
        if result['ok'] == False:
            status = '3'
        if result['ok'] == None:
            status = '4'

        component_id, cur_status = self.getComponent(name)

        if cur_status != status:
            payload =  {'status':"{0}".format(status),'description':"{0}".format(result['message'])}
            try:
               return requests.request("PUT", '{0}/components/{1}'.format(self.url, component_id), data=payload, headers=self.getHeader(), cert=self.getCert())
            except:
                self.logger.error("Cannot update cachet")
                return None
