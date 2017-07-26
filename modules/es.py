# -*- coding: utf-8 -*-

from datetime import datetime
import time
from elasticsearch import Elasticsearch

class elasticsearch:

    def __init__(self):

        self.es = Elasticsearch()


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

        res = self.es.index(index="supext-{0}".format(time.strftime("%Y.%m.%d")), doc_type='test', body=doc)
