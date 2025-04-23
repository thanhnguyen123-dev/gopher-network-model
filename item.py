from socket_utils import SocketUtils

class Item:
    def __init__(self, item_type: str, request: str, host: str, port: str):
        self.item_type = item_type
        self.request = request
        self.host = host
        self.port = port
        

    def get_item_type(self) -> str:
        return self.item_type
    
    def get_request(self) -> str:
        return self.request
    
    def get_host(self) -> str:
        return self.host
    
    def get_port(self) -> str:
        return self.port
    
    def is_external_server(self, server_host: str, server_port: int) -> bool:
        return self.host != server_host or int(self.port) != server_port
    
    def is_external_server_up(self) -> bool:
        try:
            new_sock = SocketUtils.create_socket(self.host, int(self.port))
            new_sock.close()
            return True
        except:
            return False
    

    
