#TODO implement logging (start, stop...)
#print("[ERROR] Could not create socket. Do you have permissions?")

import socket
import signal
from threading import Thread

class Proxy_IPv4:
    def __init__(self, sock_type=socket.SOCK_STREAM, dest_ip=None, dest_port=None, bind_ip="127.0.0.1", bind_port=31337, max_conn=10):
        self.sock_type = sock_type
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.bind_ip = bind_ip
        self.bind_port = bind_port
        self.max_conn = max_conn

        self.__buffsize = 4096
        self.__request_handlers = []
        self.__response_handlers = []

        # Function that gets called if dest_ip and dest_port are not set and they have to be retrieved from the application data
        # For example: HTTP requests
        self.get_dest_ip_from_data = None

        # Close socket on keyboard interrupt
        signal.signal(signal.SIGINT, self.__kill)

    def __kill(self, signal, frame):
        self.__sock.close()
        exit(1)

    def serve_forever(self):
        try:
            self.__sock = socket.socket(socket.AF_INET, self.sock_type)
            self.__sock.bind((self.bind_ip, self.bind_port))
            self.__sock.listen(self.max_conn)
        except:
            # LOG lvl:ERROR msg: permissions?
            print("err: permissions?")
            exit(1)
            # LOG lvl: INFO msg: starting service

        print("=====[ Proxy_IPv4 ]=====")
        print("listening on '%s:%d'" % (self.bind_ip, self.bind_port))
        if self.dest_ip and self.dest_port:
            print("forwarding to '%s:%d'" % (self.dest_ip, self.dest_port))
        while(1):
            (client_sock, client_addr) = self.__sock.accept()
            # LOG lvl: INFO msg: got connection from
            thread = Thread(target=self.handle_conn, args=(client_sock, *client_addr))
            thread.start()

    def add_request_handler(self, request_handler):
        self.__request_handlers.append(request_handler)

    def add_response_handler(self, response_handler):
        self.__response_handlers.append(response_handler)

    def handle_conn(self, client_sock, client_ip, client_port):
        # LOG lvl: info msg: connection from (client_ip, client_port)

        client_request_data = client_sock.recv(self.__buffsize)
        # Make request_data mutable so that handlers can change it
        dest_request_data = bytearray(client_request_data)
        #dest_request_data = client_request_data

        for request_handler in self.__request_handlers:
            request_handler(dest_request_data)

        if self.dest_ip and self.dest_port:
            dest_addr = (self.dest_ip, self.dest_port)
        elif self.get_dest_ip_from_data != None:
            dest_addr = self.get_dest_ip_from_data(dest_request_data)
        else:
            print("err no dest_addr")
            client_sock.close()
            self.__kill()
            exit(1)

        dest_sock = socket.socket(socket.AF_INET, self.sock_type)
        dest_sock.connect(dest_addr)
        dest_sock.send(dest_request_data)
        dest_response_data = dest_sock.recv(self.__buffsize)
        # Make response_data mutable so that handlers can change it
        client_response_data = bytearray(dest_response_data)

        for response_handler in self.__response_handlers:
            response_handler(client_response_data)

        client_sock.send(client_response_data)

        # TODO keep alive of connection
        dest_sock.close()
        client_sock.close()
