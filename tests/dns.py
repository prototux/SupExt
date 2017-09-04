import socket
import time
import logging

class dns:
    def test(self, config):
        ret = { 'ok': None, 'duration': 0, 'message': None }

        if not 'host' in config:
            ret['ok'] = False
            ret['message'] = 'No server to check'
            return ret

        try:
            start = time.time()
            ip = socket.gethostbyname(config['host'])
            roundtrip = int((time.time() - start)*1000)

            # If there's optional parameter ip
            if config.get('ip') and ip != config.get('ip'):
                ret['ok'] = False
                ret['message'] = 'Resolved to wrong IP {0} instead of {1}'.format(ip, config['ip'])
                return ret
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot resolve dns'
            return ret

        ret['ok'] = True
        ret['message'] = "Resolved in {0}ms".format(roundtrip)
        ret['duration'] = roundtrip
        return ret

    def __init__(self):
        self.socket = socket.socket()
