# -*- coding: utf-8 -*-

from datetime import datetime
import time
import logging
from elasticsearch import Elasticsearch

class elasticsearch:

    def __init__(self):
        self.es = Elasticsearch()
        self.logger = logging.getLogger('app_logger')

    def index(self, name, component, ret, location):

        doc = {
            'name': name,
            'component': component,
            'status': ret['ok'],
            'message': ret['message'],
            'duration': ret['duration'],
            'timestamp': datetime.now(),
            'location': location,
        }

        try:
            res = self.es.index(index="supext-{0}".format(time.strftime("%Y.%m.%d")), doc_type='test', body=doc)
        except:
            self.logger.error("Cannot connect to elasticsearch")
