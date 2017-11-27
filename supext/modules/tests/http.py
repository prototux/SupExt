import requests
import logging

class http:
    def __init__(self):
        # Disable requests' output
        requests.packages.urllib3.disable_warnings(requests.packages.urllib3.exceptions.InsecureRequestWarning)
        requests_logger = logging.getLogger('requests')
        requests_logger.setLevel(logging.ERROR)

    def run(self, config):
        ret = { 'ok': None, 'message': None }

        if not 'url' in config:
            ret['ok'] = False
            ret['message'] = 'No url to check'
            return ret

        try:
            req = requests.get(config['url'], verify=False)
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot connect to server'
            return ret

        ret['ok'] = (True if req.status_code == 200 else None) 
        ret['message'] = "Returned {0}".format(req.status_code)
        return ret
