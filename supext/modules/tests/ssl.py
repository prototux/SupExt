import ssl
import OpenSSL

class https:
    def run(self, config):
        ret = { 'ok': None, 'message': None }

        # Check for mandatory parameters
        if not 'host' in config:
            ret['ok'] = False
            ret['message'] = 'No server to check'
            return ret

        # Fetch and verify SSL certificate
        try:
            pem = ssl.get_server_certificate((config['host'], config.get('port', 443)))
            cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_PEM, pem)
        except:
            ret['ok'] = False
            ret['message'] = 'Cannot get certificate'
            return ret

        if cert.has_expired():
            ret['ok'] = False
            ret['message'] = 'Certificate has expired'
        else:
            ret['ok'] = True
            ret['message'] = 'Certificate is OK'
        return ret
