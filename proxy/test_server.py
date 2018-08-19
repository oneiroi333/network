import socket
from threading import Thread

ip = "127.0.0.1"
port = 8080
srv_msg = "server hello\n"

def main():
    local_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    local_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    local_sock.bind((ip, port))
    local_sock.listen(10)

    print("=====[ Test server ]=====")
    print("listening on port %d..." % port)
    while True:
        new_sock, addr = local_sock.accept()
        thread = Thread(target=handle_conn, args=(new_sock, addr))
        thread.start()


def handle_conn(sock, addr):
    while True:
        data = sock.recv(4096)

        print("%s:%d >> %s:%d" % (*(addr), ip, port))
        print(data.decode())

        sock.send(bytes(srv_msg.encode()))
        print("%s:%d >> %s:%d" % (ip, port, *(addr)))
        print(srv_msg)

        if not data:
            print("closing connection to: %s:%d" % (addr[0], addr[1]))
            sock.close()
            break

if __name__ == "__main__":
    main()
