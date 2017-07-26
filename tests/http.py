import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning
import time
import logging

class http:

    def test(self, config):
        ret = { 'ok': None, 'duration': 0, 'message': None }

        if not 'url' in config:
            ret['ok'] = False
            ret['message'] = 'No url to check'
            return ret

        try:
            start = time.time()
            req = requests.get(config['url'], verify=False)
            roundtrip = int((time.time() - start)*1000)
        except requests.exceptions.RequestException as e:
            ret['ok'] = False
            ret['message'] = 'Cannot connect to server'
            return ret
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot connect to server'
            return ret

        if req.status_code==200:
            ret['ok'] = True
        else:
            ret['ok'] = None

        ret['message'] = "Returned {0} in {1}ms".format(req.status_code, roundtrip)
        ret['duration'] = roundtrip
        return ret

    def __init__(self):
        requests.packages.urllib3.disable_warnings(InsecureRequestWarning)
        requests_logger = logging.getLogger('requests')
        requests_logger.setLevel(logging.CRITICAL)
