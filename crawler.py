import socket
from socket import *

HOST = "comp3310.ddns.net"
PORT = 70

def fetch_root_menu():
    sock = socket(AF_INET, SOCK_STREAM)
    sock.settimeout(5)

    sock.connect((HOST, PORT))

    sock.sendall(b"\r\n")

    data = b""
    while True:
        chunk = sock.recv(4096)
        if not chunk:
            break
        data += chunk

    sock.close()
    # return data.decode(x"utf-8", errors="replace")
    return data.decode("utf-8")
    
    
if __name__ == "__main__":
    menu = fetch_root_menu()
    print(menu)
