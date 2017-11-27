# -*- coding: utf-8 -*-
import subprocess
import os
import csv

class crl:
    def __init__(self):
        self.script = '''
            FILE="/tmp/crl-$(echo "{0}" | base64).der"
            if [[ $(curl -w "%{{http_code}}" -m 5 -sSLo "$FILE" "{0}" 2>/dev/null) != "200" ]]; then exit 210; fi
            if [[ ! -f "$FILE" ]]; then exit 210; fi
            dolu=$(openssl crl -inform DER -in "$FILE" -text -noout | grep "Last Update" | cut -d" " -f11-)
            gap=$(({1} - ($(($(date -u +%s)/3600)) - $(($(date -d"$dolu" +%s)/3600)))))
            rm "$FILE"
            if [[ $gap -lt 0 ]]; then exit 211; else exit 0; fi
        '''

    def run(self, config):
        ret = { 'ok': None, 'message': '' }
        results = {}

        # Check for mandatory parameters
        if not 'crls' in config or not os.path.isfile(config['crls']):
            ret['ok'] = False
            ret['message'] = 'No CRL list'
            return ret

        with open(config['crls']) as list:
            crls = csv.reader(list, delimiter=';', quoting=csv.QUOTE_NONE)
            for item in crls:
                name = item[3]
                url = item[0]
                renew = item[2]

                # Check for CRL
                try:
                    result = subprocess.call(['bash', '-c', self.script.format(url, renew)])
                except subprocess.CalledProcessError as e:
                    results[name] = 'Script error'

                if result == 0:
                    results[name] = None
                elif result == 210:
                    results[name] = 'Cannot download CRL'
                elif result == 211:
                    results[name] = 'Out of date'

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
