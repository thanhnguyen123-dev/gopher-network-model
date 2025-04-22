from socket_utils import SocketUtils

class Item:
    def __init__(self, item_type, request, host, port):
        self.item_type = item_type
        self.request = request
        self.host = host
        self.port = port

    def get_item_type(self):
        return self.item_type
    
    def get_request(self):
        return self.request
    
    def get_host(self):
        return self.host
    
    def get_port(self):
        return self.port
    
    def is_external_server(self, server_host, server_port):
        return self.host != server_host or int(self.port) != server_port
    
    def is_external_server_up(self):
        try:
            new_sock = SocketUtils.create_socket(self.host, int(self.port))
            new_sock.close()
            return True
        except:
            return False
    

    
