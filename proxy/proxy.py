#TODO implement logging (start, stop...)
#print("[ERROR] Could not create socket. Do you have permissions?")

import socket
from threading import Thread

class Proxy_IPv4:
    def __init__(self, sock_type=socket.SOCK_STREAM, dest_ip_addr=None, dest_port=None, ip_addr="127.0.0.1", port=31337, max_conn=10):
        self.sock_type = sock_type
        self.dest_ip_addr = dest_ip_addr
        self.dest_port = dest_port
        self.ip_addr = ip_addr
        self.port = port
        self.max_conn = max_conn
        self.buffsize = 4096
        self.state = "STOPPED"
        self.request_handlers = []
        self.response_handlers = []
        self.get_remote_addr = None

    def start(self):
        if self.state != "RUNNING":
            self.state = "RUNNING"
            try:
                self.sock = socket.socket(socket.AF_INET, self.sock_type)
                self.sock.bind((self.ip_addr, self.port))
                self.sock.listen(self.max_conn)
            except:
                # LOG lvl:ERROR msg: permissions?
                print("err: permissions?")
                exit(1)
                # LOG lvl: INFO msg: starting service

            print("running...")
            while(1):
                (client_sock, client_addr) = self.sock.accept()
                # LOG lvl: INFO msg: got connection from
                thread = Thread(target=self.handle_conn, args=(client_sock, *client_addr))
                thread.start()

    def stop(self):
        if self.state == "RUNNING":
            self.state = "STOPPED"
            socket.close(self.sock)
            # LOG lvl: INFO msg: stopping service
            print("stopped")

    def add_request_handler(self, request_handler):
        self.request_handlers.append(request_handler)

    def add_response_handler(self, response_handler):
        self.response_handlers.append(response_handler)

    def handle_conn(self, client_sock, client_ip, client_port):
        # LOG lvl: info msg: connection from (client_ip, client_port)

        client_request_data = client_sock.recv(self.buffsize)
        # Make request_data mutable so that handlers can change it
        remote_request_data = bytearray(client_request_data)

        for request_handler in self.request_handlers:
            request_handler(remote_request_data)

        if self.dest_ip_addr and self.dest_port:
            remote_addr = (self.dest_ip_addr, self.dest_port)
        elif self.get_remote_addr != None:
            remote_addr = self.get_remote_addr(remote_request_data)
        else:
            client_sock.close()
            exit(1)

        remote_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        remote_sock.connect(remote_addr)
        remote_sock.send(remote_request_data)
        remote_response_data = remote_sock.recv(self.buffsize)
        # Make response_data mutable so that handlers can change it
        client_response_data = bytearray(remote_response_data)

        for response_handler in self.response_handlers:
            response_handler(client_response_data)

        client_sock.send(client_response_data)

        # Close both ends
        remote_sock.close()
        client_sock.close()
