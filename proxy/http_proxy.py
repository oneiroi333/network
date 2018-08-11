from proxy import *

class HTTP_Proxy_IPv4(Proxy_IPv4):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def get_remote_addr(self, data):
        host_start = data.find("Host:")
        host = data[host_start+6:]
        ip_addr = socket.gethostbyname(host)
        return (ip_addr, 80)
