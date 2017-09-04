import subprocess
import sys
import time
import os
import logging

class shell:
    def test(self, config):
        ret = { 'ok': None, 'message': '', 'duration': 0 }

        if not 'cmd' in config:
            ret['ok'] = False
            ret['message'] = 'No command to execute'
            return ret

        try:
            result = subprocess.check_output(config['cmd'])
        except subprocess.CalledProcessError:
            result = ''

        if result.find('OK') != -1:
            ret['ok'] = True
            if result.find(':') != -1:
                ret['message'] = 'OK in {0}ms'.format(result.split(':')[1])
                ret['duration'] = result.split(':')[1]
            else:
                ret['message'] = 'OK'
        elif result.find('ERROR') != -1:
            ret['ok'] = None
            ret['message'] = result
        else:
            ret['ok'] = None
            ret['message'] = 'Unknown error'

        return ret
