from socket import *
from datetime import datetime
from item import Item
from socket_utils import SocketUtils

# GopherClient class

class GopherClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host                     
        self.server_port = server_port
        self.sock = None
        self.directories = set()
        self.visited_paths = set()
        self.text_file_path_list = []
        self.binary_file_path_list = []
        self.smallest_text_file = ("", "", float('inf'))    # tuple of (path, content, size)
        self.largest_text_file = ("", 0)                    # tuple of (path, size)
        self.smallest_binary_file = ("", float('inf'))      # tuple of (path, size)
        self.largest_binary_file = ("", 0)                  # tuple of (path, size)
        self.references_with_issues = set()
        self.references_with_errors = set()
        self.external_servers = dict()

    def send_request(self, path):
        print(f"Request: {path}, time: {datetime.now()}")
        path += "\r\n"
        self.sock = SocketUtils.create_socket(self.server_host, self.server_port)
        self.sock.sendall(path.encode())
    
    def read_response(self, path):
        data = b""
        while True:
            try:
                # receive data from the server
                chunk = self.sock.recv(4096)

                # if the server has no more data to send, break
                if not chunk:
                    break
                data += chunk

                # if the response ends with .CRLF, then it is the end of the file
                if data.endswith(b".\r\n"):
                    break

            except TimeoutError:
                print("Timeout")
                self.references_with_issues.add(path)
                self.sock.close()
                raise TimeoutError
                
        # close socket since we only want one-time request
        self.sock.close()


        return data
    
    def parse_response(self, data):
        parsed_items = []

        # split into an array of lines because each line ends with a CRLF
        lines = data.split("\r\n")
        for line in lines:
            parsed_item = GopherClient.parse_item(line)
            parsed_items.append(parsed_item)

        return parsed_items


    @staticmethod
    def parse_item(line):
        # split into an array of items because each item is separated by a tab
        raw_items = line.split("\t")
        item_type = raw_items[0][0] if len(raw_items[0]) > 0 else ""
        path = raw_items[1] if len(raw_items) > 1 else ""
        host = raw_items[2] if len(raw_items) > 2 else ""
        port = raw_items[3] if len(raw_items) > 3 else ""

        return Item(item_type, path, host, port)

    
    def index_server(self, path):
        # if the path has already been visited, skip it to avoid loops
        if path in self.visited_paths:
            return
        
        self.visited_paths.add(path)
        self.directories.add(path)
        self.send_request(path)
        raw_response = self.read_response(path).decode()

        if len(raw_response) == 0:
            return

        items = self.parse_response(raw_response)
        for item in items:
            # extract item attributes
            item_type = item.get_item_type()
            item_path = item.get_request()
            item_host = item.get_host()
            item_port = item.get_port()

            # item-type i (informational text)
            if item_type == "i":
                continue

            # item-type 3 (error)
            if item_type == "3":
                self.references_with_errors.add(item_path)

            # EXTERNAL SERVER CASE
            elif item.is_external_server(self.server_host, self.server_port):
                if is_up := item.is_external_server_up():
                    self.external_servers[item_host] = (item_port, is_up)
                else:
                    self.references_with_issues.add(item_path)
            
            # INTERNAL SERVER CASE
            # item-type 0 (text file)
            elif item_type == "0":
                self.handle_text_file(item_path)

            # item-type 1 (directory)
            elif item_type == "1" and item_path != "" and item_path not in self.directories:
                self.index_server(item_path)
                self.directories.add(item_path)

            # non-text file
            else:
                self.handle_non_text_file(item_path)


    def handle_text_file(self, item_path):
        print(f"Text file: {item_path}")
        self.send_request(item_path)
        try:
            text_file_content = self.read_response(item_path).decode()
        except:
            return

        if item_path not in self.references_with_issues:
            self.text_file_path_list.append(item_path)

        if len(text_file_content) < self.smallest_text_file_content:
            self.smallest_text_file_content = text_file_content

        if len(text_file_content) > self.largest_text_file_size:
            

    def handle_non_text_file(self, item_path):
        print(f"Non-text file: {item_path}")

    def run(self):
        root_path = ""
        self.index_server(root_path)

