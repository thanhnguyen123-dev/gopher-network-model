from socket_utils import SocketUtils

class Item:
    def __init__(self, item_type: str, request: str, host: str, port: str):
        self.item_type = item_type
        self.request = request
        self.host = host
        self.port = port
        
    """
        Get the item type

        :return: the item type
    """
    def get_item_type(self) -> str:
        return self.item_type
    

    """
        Get the request

        :return: the request
    """
    def get_request(self) -> str:
        return self.request


    """
        Get the host

        :return: the host
    """
    def get_host(self) -> str:
        return self.host


    """
        Get the port

        :return: the port
    """
    def get_port(self) -> str:
        return self.port
    

    """
        Check if the item is an external server (not the same host or port as the main server)

        :param server_host: the host of the server
        :param server_port: the port of the server
        :return: whether the item is an external server
    """
    def is_external_server(self, server_host: str, server_port: int) -> bool:
        return self.host != server_host or int(self.port) != server_port
    

    """
        Check if the external server is up (can connect to the server)

        :return: whether the external server is up
    """
    def is_external_server_up(self) -> bool:
        try:
            new_sock = SocketUtils.create_socket(self.host, int(self.port))
            new_sock.close()
            return True
        except:
            return False
    

    
