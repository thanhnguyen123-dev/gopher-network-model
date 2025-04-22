from socket import *

class SocketUtils:
    @staticmethod
    def create_socket(host: str, port: int) -> socket:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        return sock
    