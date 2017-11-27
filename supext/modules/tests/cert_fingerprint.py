# -*- coding: utf-8 -*-
import subprocess
import csv
import os

class cert_fingerprint:
    def __init__(self):
        self.script = '''
            FILE="/tmp/cert-$(echo "{0}" | base64).crt"
            if [[ "$(curl -w "%{{http_code}}" -m 5 -sSLo "$FILE" {0} 2>/dev/null)" != "200" ]]; then exit 210; fi
            if [[ "$(du "$FILE" | cut -f 1)" == "0" ]]; then exit 211; fi
            if [[ "$(openssl x509 -noout -fingerprint -sha256 -inform der -in "$FILE" 2>&1 | cut -d"=" -f2)" != "{1}" ]]; then exit 212; fi
            rm "$FILE"
        '''

    def run(self, config):
        ret = { 'ok': None, 'message': '' }
        results = {}

        # Check for mandatory parameters
        if not 'list' in config or not os.path.isfile(config['list']):
            ret['ok'] = False
            ret['message'] = 'No certificate list'
            return ret

        with open(config['list']) as list:
            crls = csv.reader(list, delimiter=';', quoting=csv.QUOTE_NONE)
            for item in crls:
                name = item[0]
                url = item[2]
                fingerprint = item[1]
                try:
                    result = subprocess.call(['bash', '-c', self.script.format(url, fingerprint)])
                except subprocess.CalledProcessError as e:
                    results[name] = 'Script error'

                if result == 0:
                    results[name] = None
                elif result == 210:
                    results[name] = 'Cannot download certificate from {0}'.format(url)
                elif result == 212:
                    results[name] = 'Invalid certificate'
                elif result == 211:
                    results[name] = 'Empty response from server'

            # Check what case are we in
            all_ok = True
            all_failed = True
            for name, message in results.items():
                if message:
                    all_ok = False
                    ret['message'] += ' {0} -> {1} //'.format(name, message)
                else:
                    all_failed = False

            # Return
            if all_ok:
                ret['ok'] = True
                ret['message'] = 'All ok'
            elif all_failed:
                ret['ok'] = None
                ret['message'] = ' All failed'
            else:
                ret['ok'] = False

            return ret
