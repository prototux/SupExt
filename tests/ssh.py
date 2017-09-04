import time
import logging
import paramiko

class ssh:
    def test(self, config):
        ret = { 'ok': None, 'duration': 0, 'message': None }

        if not 'host' in config and user in config:
            ret['ok'] = False
            ret['message'] = 'No server to check, or missing username'
            return ret

        try:
            start = time.time()
            self.ssh.connect(config['host'], port=config.get('port', 22), username=config['user'], password=config.get('password'), key_filename=config.get('keyfile'))
            roundtrip = int((time.time() - start)*1000)
            self.ssh.close()
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot connect to server'
            return ret

        ret['ok'] = True
        ret['message'] = "Connected in {0}ms".format(roundtrip)
        ret['duration'] = roundtrip
        return ret

    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
