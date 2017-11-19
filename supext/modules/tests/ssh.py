import time
import paramiko

class ssh:
    def __init__(self):
        self.ssh = paramiko.SSHClient()
        self.ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

    def run(self, config):
        ret = { 'ok': None, 'message': None }

        # Check for mandatory parameters
        if not 'host' in config and user in config:
            ret['ok'] = False
            ret['message'] = 'No server to check, or missing username'
            return ret

        # Try to connect to SSH
        try:
            self.ssh.connect(config['host'], port=config.get('port', 22), username=config['user'], password=config.get('password'), key_filename=config.get('keyfile'))
            self.ssh.close()
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot connect to server'
            return ret

        ret['ok'] = True
        ret['message'] = "Connected correctly"
        return ret
