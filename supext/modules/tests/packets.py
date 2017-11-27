import subprocess

class packets:
    def __init__(self):
        self.script = '''
            if [[ "$(ping -c "{1}" "{0}" | grep "packet loss" | cut -d' ' -f 6 | sed 's/%//')" -gt {2} ]]; then exit 210; fi
        '''

    def run(self, config):
        ret = { 'ok': None, 'message': '' }

        # Check for mandatory parameters
        if not 'host' in config:
            ret['ok'] = False
            ret['message'] = 'No server to test'
            return ret

        try:
            # Using call instead of run because of python <3.5 compat
            result = subprocess.call(['bash', '-c', self.script.format(config['host'], config.get('pings', '10'), config.get('rate', 20))])
        except subprocess.CalledProcessError:
            ret['ok'] = False
            ret['message'] = 'Script error'
            return ret

        if result == 0:
            ret['ok'] = True
            ret['message'] = 'OK'
        elif result == 210:
            ret['ok'] = None
            ret['message'] = 'Packet loss > 20%'
        return ret
