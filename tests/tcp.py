import socket
import time
import logging

class tcp:

    def test(self, config):
        ret = { 'ok': None, 'duration': 0, 'message': None }

        if not 'host' in config:
            ret['ok'] = False
            ret['message'] = 'No server to check'
            return ret

        try:
            start = time.time()
            self.socket.connect((config['host'], config['port']))
            roundtrip = int((time.time() - start)*1000)
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot connect to server'
            return ret

        ret['ok'] = True
        ret['message'] = "Connected in {0}ms".format(roundtrip)
        ret['duration'] = roundtrip
        return ret

    def __init__(self):
        self.socket = socket.socket()
