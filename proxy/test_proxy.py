from proxy import Proxy_IPv4

def main():
    proxy = Proxy_IPv4(dest_ip="127.0.0.1", dest_port=8080, bind_ip="127.0.0.1", bind_port=31337, max_conn=5)
    proxy.add_request_handler(pretty_print_request)
    proxy.add_response_handler(pretty_print_response)
    proxy.serve_forever()


def pretty_print_request(data):
    print("*********************")
    print(' '.join('{:02x}'.format(x) for x in data))
    print("*********************")

def pretty_print_response(data):
    print("#####################")
    print(' '.join('{:02x}'.format(x) for x in data))
    print("#####################")

if __name__ == "__main__":
    main()
