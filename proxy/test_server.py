import socket
from threading import Thread

ip = "127.0.0.1"
port = 8080
srv_msg = "server hello\n"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM, proto=0)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind((ip, port))
    sock.listen(10)

    print("=====[ Test server ]=====")
    print("listening on port %d..." % port)
    while True:
        sock, addr = sock.accept()
        thread = Thread(target=handle_conn, args=(sock, addr))
        thread.start()

def handle_conn(sock, addr):
    while True:
        while True:
            data = sock.recv(4096)
            if not data:
                break
        print("%s:%d >> %s:%d" % (*(addr), ip, port))
        print(data.decode())

        sock.send(bytes(srv_msg.encode()))
        print("%s:%d >> %s:%d" % (ip, port, *(addr)))
        print(srv_msg)

        if not data:
            sock.close()
            return

if __name__ == "__main__":
    main()
