import time
import paramiko

class ssh:
    def run(self, config):
        ret = { 'ok': None, 'message': None }

        # Check for mandatory parameters
        if not 'host' in config and user in config:
            ret['ok'] = False
            ret['message'] = 'No server to check, or missing username'
            return ret

        try:
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        except:
            ret['ok'] = False
            ret['message'] = 'SSH Client error'
            return ret

        # Try to connect to SSH
        try:
            ssh_client.connect(config['host'], port=config.get('port', 22), username=config['user'], password=config.get('password'), key_filename=config.get('keyfile'))
            ssh_client.close()
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot connect to server'
            return ret

        ret['ok'] = True
        ret['message'] = "Connected correctly"
        return ret
