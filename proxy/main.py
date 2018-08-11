from http_proxy import *

def main():
    http_proxy = HTTP_Proxy_IPv4(dest_ip_addr="localhost", dest_port=8080, max_conn=5)
    http_proxy.start()

if __name__ == "__main__":
    main()
