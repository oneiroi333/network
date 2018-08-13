#TODO implement logging (start, stop...)
#print("[ERROR] Could not create socket. Do you have permissions?")

import socket
import ssl
from threading import Thread

class Proxy_IPv4:
    def __new__(cls, sock_type=socket.SOCK_STREAM, dest_ip=None, dest_port=None, local_ip="127.0.0.1", local_port=31337, max_conn=10, ssl=False, parse_dest_from_data=None):
        if not (dest_ip and dest_port) or parse_dest_from_data:
            raise ValueError("specify 'dest_ip' and 'dest_port' OR callback function 'parse_dest_from_data'")
        return super(Proxy_IPv4, cls).__new__(cls)

    def __init__(self, sock_type=socket.SOCK_STREAM, dest_ip=None, dest_port=None, local_ip="127.0.0.1", local_port=31337, max_conn=10, ssl=False, parse_dest_from_data=None):
        self.sock_type = sock_type
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.local_ip = local_ip
        self.local_port = local_port
        self.max_conn = max_conn
        self.ssl = ssl
        self.ssl_client_ctx = None
        self.ssl_server_ctx = None
        self.buffsize = 4096
        self.request_handlers = []
        self.response_handlers = []
        # Function that gets called if dest_ip and dest_port are not set explicitly
        # but instead have to be parsed from the application data (e.g. HTTP request)
        self.parse_dest_from_data = parse_dest_from_data

        if self.ssl:
            self.ssl_client_ctx = ssl.create_default_context()
            self.ssl_server_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self.ssl_server_ctx.load_cert_chain('cert/certchain.pem', 'cert/private.key')

    def serve_forever(self):
        try:
            self.sock = socket.socket(socket.AF_INET, self.sock_type)
            self.sock.bind((self.local_ip, self.local_port))
            self.sock.listen(self.max_conn)
        except:
            # LOG lvl:ERROR msg: permissions?
            print("err: permissions?")
            return
            # LOG lvl: INFO msg: starting service

        print("=====[ Proxy_IPv4 ]=====")
        print("listening on '%s:%d'" % (self.local_ip, self.local_port))
        if self.dest_ip and self.dest_port:
            print("forwarding to '%s:%d'" % (self.dest_ip, self.dest_port))
        while(1):
            (client_sock, client_addr) = self.sock.accept()
            # LOG lvl: INFO msg: got connection from
            thread = Thread(target=self.handle_conn, args=(client_sock, client_addr))
            thread.start()

    def add_request_handler(self, request_handler):
        self.request_handlers.append(request_handler)

    def add_response_handler(self, response_handler):
        self.response_handlers.append(response_handler)

    def handle_conn(self, client_sock, client_addr):
        # LOG lvl: info msg: connection from (client_ip, client_port)
        dest_init = False
        while(1):
            request_data = client_sock.recv(self.buffsize)

            # Initialize dest connection once
            if not dest_init:
                dest_addr = None
                if self.dest_ip and self.dest_port:
                    dest_addr = (self.dest_ip, self.dest_port)
                elif not (self.dest_ip and self.dest_port):
                    dest_addr = self.parse_dest_from_data(request_data)
                if not dest_addr:
                    # log err msg: no dest_addr
                    client_sock.close()
                    return

                # TODO raise error when one of the following fails
                dest_sock = socket.socket(socket.AF_INET, self.sock_type)
                dest_sock.connect(dest_addr)

            if len(request_data):
                for request_handler in self.request_handlers:
                    request_data = request_handler(client_addr, request_data)
                dest_sock.send(request_data)

            response_data = dest_sock.recv(self.buffsize)
            if len(response_data):
                for response_handler in self.response_handlers:
                    response_data = response_handler(dest_addr, response_data)
                client_sock.send(response_data)

            # TODO keep alive of connection
            if not len(request_data) or not len(response_data):
                print("closing connection")
                client_sock.close()
                dest_sock.close()
                return
