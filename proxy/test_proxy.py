import socket
import proxy as p

def main():
    local_sock_info = p.sock_info(
            addr=("127.0.0.1", 31337),
            sock_opt=[(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)]
            )
    dest_sock_info = p.sock_info(addr=("127.0.0.1", 8080))

    proxy = p.proxy(local_sock_info, dest_sock_info)
    proxy.add_request_handler(pretty_print_request)
    proxy.add_response_handler(pretty_print_response)
    proxy.serve_forever()

def pretty_print_request(client_addr, data):
    print("\n[>>] %s:%d" % (client_addr[0], client_addr[1]))
    print("hex: " +  " ".join('{:02x}'.format(x) for x in data))
    print("ascii: " + bytes(data).decode())
    return data

def pretty_print_response(dest_addr, data):
    print("\n[<<] %s:%d" % (dest_addr[0], dest_addr[1]))
    print("hex: " +  " ".join('{:02x}'.format(x) for x in data))
    print("ascii: " + bytes(data).decode())
    return data

if __name__ == "__main__":
    main()
