from flask import Flask, request, Response
from flask_cors import CORS
import threading
import logging
import json

class api():
    def __init__(self, parent, config):
        # Init Flask
        self.app = Flask('supext')
        CORS(self.app)

        # Get parent and checks
        self.parent = parent
        self.checks = self.parent.checks

        # Init logging
        self.logger = logging.getLogger('supext')
        self.flask_logger = logging.getLogger('werkzeug')
        self.flask_logger.setLevel(logging.ERROR)

        # Get parameters
        self.host = config.get('host', '127.0.0.1')
        self.port = config.get('port', '8080')
        self.key = config.get('key', None)

        if not self.key:
            self.logger.error('No key found, will not run API')

        # Add URL routing rules
        self.app.add_url_rule('/', 'root', self.root, methods=['GET'])
        self.app.add_url_rule('/api/v1/checks/<name>', 'check', self.check, methods=['GET', 'POST'])
        self.app.add_url_rule('/api/v1/checks', 'checks', self.checks, methods=['GET', 'POST'])
        self.app.add_url_rule('/api/v1/muted', 'muted', self.mute, methods=['GET'])
        self.app.add_url_rule('/api/v1/mute/<name>', 'mute', self.mute, methods=['POST'])

    def run(self):
        if self.key:
            self.logger.info('Running API')
            self.app.run(host=self.host, port=self.port, threaded=True)
            return True
        else:
            self.logger.error('No key, cannot run API')
            return False

    def verifyKey(self, request):
        if not request.headers.get('X-KEY', '') == self.key:
            self.logger.warn('Somebody tried to use the API without a valid key!')
            return False
        return True

    def getCensoredCheck(self, name):
        # Get the check and return if there's no check with this name
        check = self.checks.get(name)
        if not check:
            self.logger.warn('Got check call for nonexistant check {0}'.format(name))
            return None
        check_ret = {
            'name': check['name'],
            'test': check['test'],
            'canary': check['canary'],
            'location': check['location'],
            'muted': check['muted'],
            'last_result': check['last_result']
        }
        return check_ret


    def root(self):
        return json.dumps({'result': 'OK'})

    def check(self, name):
        # Check for API key
        if not self.verifyKey(request):
            return json.dumps({'result': 'KO'}), 403

        # GET: get check information (censor config and meta) and return it
        if request.method == 'GET':
            check = self.getCensoredCheck(name)
            if not check:
                return json.dumps({'result': 'KO'}), 404
            return json.dumps({'result': 'OK', 'check': check})

        # POST: run single check and return the result
        elif request.method == 'POST':
            self.logger.info('API got check call for {0}'.format(name))
            check = self.getCensoredCheck(name)
            if check:
                result = self.checks.run(name, False)
                if result:
                    return json.dumps({'result': 'OK', 'ret': result, 'check': check})
                return json.dumps({'result': 'nodata'}), 500
            else:
                self.logger.warn('Got check call for nonexistant check {0}'.format(name))
                return json.dumps({'result': 'KO'}), 404

        # Should never go there
        return json.dumps({'result', 'KO'})

    def checks(self):
        # Check for API key
        if not self.verifyKey(request):
            return json.dumps({'result': 'KO'}), 403

        # GET: get all checks, censor config and meta
        if request.method == 'GET':
            checks = []
            for check in self.checks.getAll():
                checks.append(self.getCensoredCheck(check['name']))
            return json.dumps({'result': 'OK', 'checks': checks})

        # POST: schedule a new check now
        elif request.method == 'POST':
            try:
                self.parent.scheduler.cancel(self.parent.round)
            except (ValueError):
                pass

            self.parent.scheduler.enter(1, 1, self.parent.loop, ())
            return json.dumps({'result': 'OK'})

        # Should never go there
        return json.dumps({'result', 'KO'})

    def mute(self, name=None):
        # Check for API key
        if not self.verifyKey(request):
            return json.dumps({'result': 'KO'}), 403

        # GET: list muted checks
        if not name and request.method == 'GET':
            checks = []
            for check in self.checks.getMuted():
                checks.append(self.getCensoredCheck(check['name']))
            return json.dumps({'result': 'OK', 'checks': checks})

        # POST: mute a check or location
        elif name and request.method == 'POST':
            if self.checks.mute(name, request.form.get('duration')):
                return json.dumps({'result': 'OK'})
            else:
                return json.dumps({'result': 'KO'})

        # Should never go there
        return json.dumps({'result', 'KO'})
