#TODO implement logging (start, stop...)
#TODO handle socket exceptions
#TODO keep alive of connections ???
#TODO SSL implementation

import socket
import signal
import ssl
from threading import Thread

class sock_info:
    def __init__(self, addr_family=socket.AF_INET, sock_type=socket.SOCK_STREAM, proto=0, addr=("127.0.0.1", 31337), sock_opt=[]):
        self.addr_family = addr_family
        self.sock_type = sock_type
        self.proto = proto
        self.addr = addr
        self.sock_opt = sock_opt # List of tuples: [(sock_opt_lvl, sock_opt_name, sock_opt_val)]

class proxy:
    def __new__(cls, local_sock_info=None, dest_sock_info=None, ssl_local=False, ssl_dest=False, ssl_path_cert="", ssl_path_pr_key=""):
        if not (local_sock_info and dest_sock_info):
            raise ValueError("Specify local and destination socket information")
        return super(proxy, cls).__new__(cls)

    def __init__(self, local_sock_info=None, dest_sock_info=None, ssl_local=False, ssl_dest=False, ssl_path_cert="", ssl_path_pr_key=""):
        self._local_sock = None
        self._open_socks = []
        self._local_sock_info = local_sock_info
        self._dest_sock_info = dest_sock_info
        self._ssl_dest_ctx = None
        self._ssl_local_ctx = None
        self._request_handlers = []
        self._response_handlers = []
        self._ssl_local = ssl_local
        self._ssl_dest = ssl_dest
        self._ssl_path_cert = ssl_path_cert
        self._ssl_path_pr_key = ssl_path_pr_key

        self.max_conn = 10
        self.bufsize = 4096
        # Callback function if dest_addr has to be parsed from the application data (e.g. HTTP request)
        self.parse_dest_addr_from_data = None

        if self._ssl_local:
            self._ssl_local_ctx = ssl.create_default_context()
        if self._ssl_dest:
            self._ssl_dest_ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            self._ssl_dest_ctx.load_cert_chain('cert/certchain.pem', 'cert/private.key')

        signal.signal(signal.SIGINT, self._sigint_handler)

    def __del__(self):
        self._clean_up()

    def _sigint_handler(self, signal, frame):
        self._clean_up(force=True)

    def _clean_up(self, force=False):
        try:
            if force:
                self._local_sock.shutdown(socket.SHUT_RDWR)
            else:
                self._local_sock.close()
        except:
            pass
        for sock in self._open_socks:
            try:
                if force:
                    sock.shutdown(socket.SHUT_RDWR)
                else:
                    sock.close()
            except:
                pass

    def _close_sock(self, sock):
        sock.close()
        try:
            for s in self._open_socks:
                if s == sock:
                    self._open_socks.remove(s)
        except:
            pass

    def _receive_from(self, sock):
        buf = ""
        try:
            while True:
                data = sock.recv(self.bufsize)
                if not data:
                    break
                buf += data
        except:
            pass
        return buf

    def _handle_conn(self, client_sock, client_addr):
        print("[INFO] Got connection from: " + str(client_addr))
        # LOG lvl: info msg: connection from (client_addr)
        self._open_socks.append(client_sock)

        # Read first request
        request_data = self._receive_from(client_sock)
        if request_data:
            for request_handler in self.request_handlers:
                request_data = request_handler(client_addr, request_data)
            dest_sock.send(request_data)

        # If the destination should be parsed from the request data, do it now
        if self.parse_dest_addr_from_data:
            dest_addr = self.parse_dest_addr_from_data(request_data)
        else:
            dest_addr = self._dest_sock_info.addr

        dest_sock = socket.socket(self._dest_sock_info.addr_family, self._dest_sock_info.sock_type, self._dest_sock_info.proto)
        if self._dest_sock_info.sock_opt:
            for sock_opt_lvl, sock_opt_name, sock_opt_val in self._dest_sock_info.sock_opt:
                dest_sock.setsockopt(sock_opt_lvl, sock_opt_name, sock_opt_val)
        self._open_socks.append(dest_sock)
        dest_sock.connect(dest_addr)
        print("[INFO] Connecting to: " + str(dest_addr))

        # Enter proxy loop
        while True:
            response_data = self._receive_from(dest_sock)
            if response_data:
                for response_handler in self._response_handlers:
                    response_data = response_handler(client_addr, response_data)
                client_sock.send(response_data_data)

            request_data = self._receive_from(client_sock)
            if request_data:
                for request_handler in self._request_handlers:
                    request_data = request_handler(client_addr, request_data)
                dest_sock.send(request_data)

            if not (request_data or response_data):
                self._close_sock(client_sock)
                self._close_sock(dest_sock)
                return

    def serve_forever(self):
        try:
            self._local_sock = socket.socket(self._local_sock_info.addr_family, self._local_sock_info.sock_type, self._local_sock_info.proto)
            if self._local_sock_info.sock_opt:
                for sock_opt_lvl, sock_opt_name, sock_opt_val in self._local_sock_info.sock_opt:
                    self._local_sock.setsockopt(sock_opt_lvl, sock_opt_name, sock_opt_val)
            self._local_sock.bind(self._local_sock_info.addr)
            self._local_sock.listen(self.max_conn)
        except OSError as err:
            # LOG lvl:ERROR msg: permissions?
            # raise exception
            print(err)
            return

        # LOG lvl: INFO msg: starting service
        # TODO log the following instead of printing
        print("[INFO] Proxy running...")

        while True:
            (client_sock, client_addr) = self._local_sock.accept()
            # LOG lvl: INFO msg: got connection from
            conn_thread = Thread(target=self._handle_conn, args=(client_sock, client_addr))
            conn_thread.start()

    def add_request_handler(self, request_handler):
        self._request_handlers.append(request_handler)

    def add_response_handler(self, response_handler):
        self._response_handlers.append(response_handler)
