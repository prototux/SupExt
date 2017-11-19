import subprocess

class shell:
    def run(self, config):
        ret = { 'ok': None, 'message': None}

        # Check for mandatory config
        if not 'cmd' in config:
            ret['ok'] = False
            ret['message'] = 'No command to execute'
            return ret

        # Execute command
        try:
            result = subprocess.run(['bash', '-c', config['cmd']])
        except subprocess.CalledProcessError:
            ret['ok'] = None
            ret['message'] = 'Script error'

        # Check for return code
        if result.returncode == 0:
            ret['ok'] = True
            ret['message'] = 'OK'
        else:
            ret['ok'] = None
            ret['message'] = 'Script returned {0}'.format(result.returncode)

        return ret
