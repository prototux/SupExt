import subprocess

class traceroute:
    def __init__(self):
        self.script = '''
            if [[ "$(sudo traceroute -I -m "{1}" "{0}" | tail -n 1 | cut -d' ' -f 3)" != "{0}" ]]; then exit 210; fi
        '''

    def run(self, config):
        ret = { 'ok': None, 'message': '' }

        # Check for mandatory parameters
        if not 'host' in config:
            ret['ok'] = False
            ret['message'] = 'No server to test'
            return ret

        try:
            result = subprocess.call(['bash', '-c', self.script.format(config['host'], config.get('hops', 30))])
        except subprocess.CalledProcessError:
            ret['ok'] = False
            ret['message'] = 'Script error'
            return ret

        if result == 0:
            ret['ok'] = True
            ret['message'] = 'OK'
        elif result == 210:
            ret['ok'] = None
            ret['message'] = 'Cannot reach host'
        return ret
