import socket

class tcp:
    def __init__(self):
        self.socket = socket.socket()

    def run(self, config):
        ret = { 'ok': None, 'message': None }

        # Check for mandatory parameters
        if not 'host' in config or not 'port' in config:
            ret['ok'] = False
            ret['message'] = 'Missing host or port'
            return ret

        # Try to connect
        try:
            self.socket.connect((config['host'], config['port']))
            ret['ok'] = True
            ret['message'] = 'Connected successfuly'
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot connect to server'
        return ret
