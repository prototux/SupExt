# -*- coding: utf-8 -*-
import subprocess

class tsa:
    def __init__(self):
        self.script = '''
            FILE="/tmp/response-$(echo "{0}" | base64).tsr"
            if [[ "$(echo "T" | openssl ts -query -sha256 -no_nonce | curl -w "%{{http_code}}" -m 15 --connect-timeout 15 -sSH 'Content-Type: application/timestamp-query' --data-binary @- "{0}" -o "$FILE")" != "200" ]]; then exit 210; fi
            if [[ ! -f "$FILE" ]]; then exit 211; fi
            gap=$(( $(date -u "+%s") - $(date -u -d "$(openssl ts -reply -in "$FILE" -text | grep "Time stamp" | cut -d' ' -f3-6)" "+%s") ))
            rm "$FILE"
            if [[ "$gap" -le "-15" ]] || [[ "$gap" -ge "15" ]]; then exit 212; fi
        '''

    def run(self, config):
        ret = { 'ok': None, 'message': '' }

        # Check for mandatory parameters
        if not 'url' in config:
            ret['ok'] = False
            ret['message'] = 'No URL to check'
            return ret

        try:
            result = subprocess.call(['bash', '-c', self.script.format(config['url'])])
        except:
            ret['ok'] = False
            ret['message'] = 'Script error'
            return ret

        if result == 0:
            ret['ok'] = True
            ret['message'] = 'OK'
        elif result == 210:
            ret['ok'] = None
            ret['message'] = 'Server unavailable'
        elif result == 212:
            ret['ok'] = False
            ret['message'] = 'Invalid timestamp'
        elif result == 211:
            ret['ok'] = None
            ret['message'] = 'No Timestamp response'
        return ret
