from socket import *
from datetime import datetime

class SocketUtils:
    @staticmethod
    def create_socket(host, port):
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        return sock
    