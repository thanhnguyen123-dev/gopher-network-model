import socket
from socket import *
from datetime import datetime

# GopherClient class
# Handles the connection to the gopher server and the parsing of the response
class GopherClient:
    def __init__(self):
        self.sock = None
        self.directories = set()
        self.text_file_path_list = []
        self.binary_file_path_list = []
        self.smallest_text_file_content = ""
        self.largest_text_file_size = 0
        self.smallest_binary_file_size = float('inf')
        self.largest_binary_file_size = 0
        self.invalid_references = set()
        self.error_references = set()

    def create_socket(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect(("comp3310.ddns.net", 70))

    def format_date_time(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def send_client_request(self, request):
        print(f"Request: {request}, time: {self.format_date_time()}")
        request += "\r\n"
        self.create_socket()
        self.sock.sendall(request.encode())
    
    def read_server_response(self, path, binary=True):
        data = b""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk

                if data.endswith(b".\r\n"):
                    break


            except timeout:
                print("Timeout")
                self.error_references.add(path)
                break

        self.sock.close()

        return data.decode()
    
    def run(self):
        self.send_client_request(".")
        print(self.read_server_response())
        
if __name__ == "__main__":
    client = GopherClient()
    client.run()
 
