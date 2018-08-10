#TODO implement logging (start, stop...)
#print("[ERROR] Could not create socket. Do you have permissions?") import socket class Proxy:
    def __init__(self, addr_family, sock_type, ip_addr, port, max_conn):
        self.addr_family = addr_family
        self.sock_type = sock_type
        self.ip_addr = ip_addr
        self.port = port
        self.conn = conn
        self.state = "STOPPED"
        self.request_handlers = []
        self.response_handlers = []
        # TODO blacklists for request-response src ip
            
    def start(self):
        if self.state != "RUNNING":
            self.state = "RUNNING"
            try:
                self.sock = socket.socket(self.addr_family, self.
                socket.bind(self.ip_addr)
                socket.listen(self.max_conn)
            except:
                # LOG lvl:ERROR msg: permissions?
                exit(1)
            
                # LOG lvl: INFO msg: starting service
            while(1):
                socket.accept()

    def stop(self):
        if self.state == "RUNNING":
            self.state = "STOPPED"
            socket.close(self.sock)
            # LOG lvl: INFO msg: stopping service

    def add_request_handler(self, request_handler):
        self.request_handlers.append(request_handler)

    def add_response_handler(self, response_handler)
        self.response_handlers.append(response_handler)

