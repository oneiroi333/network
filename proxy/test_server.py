import socket
from threading import Thread

ip = "localhost"
port = 8080
srv_msg = "server hello\n"

def main():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind((ip, port))
    sock.listen(10)

    print("=====[ Test server ]=====")
    print("listening on port %d..." % port)
    while(1):
        (sock, addr) = sock.accept()
        thread = Thread(target=handle_conn, args=(sock, addr))
        thread.start()

def handle_conn(sock, addr):
    data = sock.recv(4096)
    if not len(data):
        sock.close()
        return
    print("%s:%d >> %s:%d" % (*(addr), ip, port))
    print(data.decode())

    sock.send(bytes(srv_msg.encode()))
    print("%s:%d >> %s:%d" % (ip, port, *(addr)))
    print(srv_msg)

if __name__ == "__main__":
    main()
