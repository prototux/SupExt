import socket
import time
import logging
import random
import struct

class trace:

    def test(self, config):
        ret = { 'ok': None, 'duration': 0, 'message': None }

        if not 'host' in config:
            ret['ok'] = False
            ret['message'] = 'No server to check'
            return ret

        try:
            host = socket.gethostbyname(config['host'])
        except socket.error:
            ret['ok'] = False
            ret['message'] = "Host not found"
            return ret
        hops = config.get('hops', 30)
        port = config.get('port', random.choice(range(33434, 33535)))
        ttl = 1
        lastaddr = ''

        while True:
            receiver = socket.socket(family=socket.AF_INET,
                    type=socket.SOCK_RAW,
                    proto=socket.IPPROTO_ICMP)

            timeout = struct.pack("ll", 5, 0)
            receiver.setsockopt(socket.SOL_SOCKET, socket.SO_RCVTIMEO, timeout)

            try:
                receiver.bind(('', port))
            except socket.error:
                ret['ok'] = None
                ret['message'] = "Cannot bind"
                return ret

            sender = socket.socket(family=socket.AF_INET,
                    type=socket.SOCK_DGRAM,
                    proto=socket.IPPROTO_UDP)

            sender.setsockopt(socket.SOL_IP, socket.IP_TTL, ttl)
            sender.sendto(b'', (host, port))

            addr = None
            try:
                data, addr = receiver.recvfrom(1024)
            except socket.error:
                pass
            finally:
                receiver.close()
                sender.close()

            # We reached our host, everything is OK
            if addr and addr[0] == host:
                ret['ok'] = True
                ret['message'] = "Can reach the host"
                return ret

            # Get last addr for diagnostics
            if addr:
                lastaddr = addr[0]

            # Cannot reach with x hops, that's a fail
            if ttl == hops:
                ret['ok'] = False
                ret['message'] = "Last reached: {0}".format(lastaddr)
                return ret

            ttl += 1
