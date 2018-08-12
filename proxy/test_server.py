import socket

def main():
    ip = "localhost"
    port = 8080
    srv_msg = "hello from server"

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen(10)

    print("=====[ Test server ]=====")
    print("listening on port %d..." % port)
    while(1):
        (conn, client_addr) = sock.accept()
        data = conn.recv(4096)
        print("%s:%d >> %s:%d" % (*(client_addr), ip, port))
        print(data)

        conn.send(bytes(srv_msg.encode()))
        print("%s:%d >> %s:%d" % (ip, port, *(client_addr)))
        print(srv_msg)

        conn.close()

if __name__ == "__main__":
    main()
