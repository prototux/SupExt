import time
import logging
from datetime import datetime
from elasticsearch import Elasticsearch

class elasticsearch:
    def __init__(self, config):
        self.es = Elasticsearch(config.get('hosts', ['localhost:443']))
        self.logger = logging.getLogger('supext')

    def run(self, result, check):
        doc = {
            'name': check['name'],
            'status': result['ok'],
            'message': result['message'],
            'timestamp': datetime.now(),
            'location': check['location']
        }

        try:
            res = self.es.index(index="supext-{0}".format(time.strftime("%Y.%m.%d")), doc_type='test', body=doc)
        except:
            self.logger.error("Cannot connect to elasticsearch")
