# -*- coding: utf-8 -*-
import subprocess

class ocsp:
    def __init__(self):
        self.script = '''
            if [[ ! -f "{1}" || ! -f "{2}" ]]; then exit 210; fi;
            if [[ $(curl -w "%{{http_code}}" -sSL "{0}" -o /dev/null) != "200" ]]; then exit 211; fi;
            if [[ $(openssl ocsp -issuer "{2}" -cert "{1}" -url "{0}" -text -noverify | egrep -c ".*\.(pem|cer): (revoked|good|unknown)") -eq 0 ]]; then exit 212; fi
        '''

    def run(self, config):
        ret = { 'ok': None, 'message': '' }

        # Check for mandatory parameters
        if not config.get('url') or not config.get('certificate') or not config.get('issuer'):
            ret['ok'] = False
            ret['message'] = 'No URL to check or missing certificates'
            return ret

        try:
            result = subprocess.call(['bash', '-c', self.script.format(config['url'], config['certificate'], config['issuer'])])
        except subprocess.CalledProcessError as e:
            ret['ok'] = False
            ret['message'] = 'Script error'
            return ret

        if result == 0:
            ret['ok'] = True
            ret['message'] = 'OK'
        elif result == 211:
            ret['ok'] = None
            ret['message'] = 'Server unavailable'
        elif result == 212:
            ret['ok'] = False
            ret['message'] = 'Invalid OCSP response'
        elif result == 210:
            ret['ok'] = None
            ret['message'] = 'No test files'
        else:
            ret['ok'] = None
            ret['message'] = 'Unknown error'
        return ret
