import socket

class dns:
    def __init__(self):
        self.socket = socket.socket()

    def run(self, config):
        ret = { 'ok': None, 'message': None }

        # Check for mandatory parameters
        if not 'host' in config:
            ret['ok'] = False
            ret['message'] = 'No server to check'
            return ret

        # Try to resolve DNS
        try:
            ip = socket.gethostbyname(config['host'])

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
        ret['message'] = "Resolved correctly"
        return ret
