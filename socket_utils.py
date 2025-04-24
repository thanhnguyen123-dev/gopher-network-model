from socket import *

class SocketUtils:
    """
        Create a socket

        :param host: the host of the socket
        :param port: the port of the socket
        :return: the socket
    """
    @staticmethod
    def create_socket(host: str, port: int) -> socket:
        sock = socket(AF_INET, SOCK_STREAM)
        sock.settimeout(5)
        sock.connect((host, port))
        return sock
    