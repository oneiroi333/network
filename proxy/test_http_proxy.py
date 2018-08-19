import socket
import sys
import proxy as p

def main():
    if len(sys.argv) != 3:
        print("Usage: %s <ip> <port>" % (sys.argv[0]))
        sys.exit(1)
    ip = sys.argv[1]
    port = int(sys.argv[2]

    local_sock_info = p.sock_info( addr=(ip, port), sock_opt=[(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)])
    dest_sock_info = p.sock_info(addr=(None, None))

    proxy = p.proxy(local_sock_info, dest_sock_info)
    proxy.parse_dest_addr_from_data = addr_from_http_req
    proxy.add_request_handler(print_it)
    proxy.add_response_handler(print_it)
    proxy.serve_forever()

def addr_from_http_req(http_request):
    req = http_request.decode()
    for line in req.splitlines():
        host_str = line.find("Host: ")
        if host_str > -1:
            hostname = line[host_str + 6:line.find("\n")]
    ip = socket.gethostbyname(hostname)
    return (ip, 80)

def print_it(addr, data):
    print("=====[ From: %s:%d ]=====" % (addr[0], addr[1]))
    print(data.decode())

if __name__ == "__main__":
    main()
