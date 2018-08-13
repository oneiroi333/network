from proxy import Proxy_IPv4

def main():
    proxy = Proxy_IPv4(dest_ip="127.0.0.1", dest_port=8080, local_ip="127.0.0.1", local_port=31337, max_conn=5)
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
