from socket import *
from datetime import datetime
from item import Item
from socket_utils import SocketUtils
from time import time
import os
from file_stats import FileStats

"""
    A class to index a Gopher server

    :param server_host: the host of the Gopher server
    :param server_port: the port of the Gopher server
"""
class GopherClient:
    TIME_OUT = 20                   #timeout in seconds
    EOF_TERMINATOR = b".\r\n"       #.<CRLF>
    CRLF = "\r\n"                   #<CRLF>
    TAB = "\t"                      #<TAB>
    MAX_FILENAME_LENGTH = 255       #maximum filename length

    # constructor
    def __init__(self, server_host, server_port):
        self.server_host = server_host                     
        self.server_port = server_port
        self.sock = None
        self.directories = set()
        self.visited_paths = set()
        self.text_file_path_list = []
        self.binary_file_path_list = []
        self.smallest_text_file = FileStats("", float('inf'), None)
        self.largest_text_file = FileStats("", 0, None)
        self.smallest_binary_file = FileStats("", float('inf'), None)
        self.largest_binary_file = FileStats("", 0, None)
        self.references_with_issues = set()
        self.references_with_errors = set()
        self.external_servers = dict()


    """
        Send a request to the Gopher server and print the request path and timestamp

        :param path: the request path to send to the Gopher server
    """
    def send_request(self, path: str) -> None:
        print(f"Request: {path} @ Time: {datetime.now()}")
        path += GopherClient.CRLF
        self.sock = SocketUtils.create_socket(self.server_host, self.server_port)
        self.sock.sendall(path.encode())
    

    """
        Read the response from the Gopher server

        :param path: the path to read the response from
        :param is_text_file: whether the response is a text file or not
        :return: the response from the Gopher server
    """
    def read_response(self, path: str, is_text_file: bool = False) -> bytes:
        data = b""

        start_time = time()
        
        while True:
            if time() - start_time > GopherClient.TIME_OUT:
                # if the file is potentially too large, add it to the references with issues
                print(f"Timeout: {path} @ Time: {datetime.now()}, file is potentially too large")
                self.references_with_issues.add(path)
                self.sock.close()
                raise TimeoutError

            try:
                # receive data from the server
                chunk = self.sock.recv(4096)

                # if the server has no more data to send, break
                if not chunk:
                    break
                data += chunk

                # if the response ends with .<CRLF>, then it is the end of the file
                if data.endswith(GopherClient.EOF_TERMINATOR):
                    break

            except (socket.timeout, TimeoutError):
                print("Timeout")
                self.references_with_issues.add(path)
                self.sock.close()
                raise TimeoutError
                
        # close socket since we only want one-time request
        self.sock.close()
      
        if is_text_file:
            # if the file is a text file, remove the .<CRLF> and return the payload
            if data.endswith(GopherClient.EOF_TERMINATOR):
                payload = data[:-len(GopherClient.EOF_TERMINATOR)].rstrip(GopherClient.CRLF.encode())
                return payload
            else:
                # if the file is not a text file, add it to the references with issues
                self.references_with_issues.add(path)
                return data
        else:
            # if the file is not a text file, return the payload
            return data


    """
        Parse the response from the Gopher server

        :param data: the response from the Gopher server
        :return: the parsed items from the response
    """
    def parse_response(self, data: str) -> list[Item]:
        parsed_items = []

        # split into an array of lines because each line ends with a <CRLF>
        lines = data.split(GopherClient.CRLF)
        for line in lines:
            parsed_item: Item = self.parse_item(line)
            parsed_items.append(parsed_item)

        return parsed_items


    """
        Parse the response from the Gopher server

        :param line: the line to parse into an item
        :return: the parsed item from the line
    """
    def parse_item(line: str) -> Item:
        # split into an array of items because each item is separated by a tab
        raw_items = line.split(GopherClient.TAB)
        item_type = raw_items[0][0] if len(raw_items[0]) > 0 else ""
        path = raw_items[1] if len(raw_items) > 1 else ""
        host = raw_items[2] if len(raw_items) > 2 else ""
        port = raw_items[3] if len(raw_items) > 3 else ""

        return Item(item_type, path, host, port)

    
    """
        Index the Gopher server recursively by exploring all the directories and files

        :param path: the path to index
    """
    def index_server(self, path: str) -> None:
        # if the path has already been visited, skip it to avoid loops or traps
        if path in self.visited_paths:
            return
        
        self.visited_paths.add(path)
        self.directories.add(path)
        self.send_request(path)
        raw_response = self.read_response(path).decode()

        # if the response is empty, skip it
        if len(raw_response) == 0:
            return

        # parse the response into items
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
                self.references_with_errors.add(path)
                continue

            # EXTERNAL SERVER CASE
            if item.is_external_server(self.server_host, self.server_port):
                if is_up := item.is_external_server_up():
                    self.external_servers[item_host] = (item_port, is_up)
                    continue
                else:
                    self.references_with_issues.add(item_path)
                    continue
            
            # INTERNAL SERVER CASE
            # item-type 0 (text file)
            if item_type == "0":
                self.handle_text_file(item_path)

            # non-text file
            elif item_type != "i" and item_type != "1":
                self.handle_non_text_file(item_path)

            # item-type 1 (directory)
            elif item_type == "1" and item_path != "" and item_path not in self.directories:
                self.index_server(item_path)
                self.directories.add(item_path)


    """
        Handle a text file by sending a request to the Gopher server, reading the response, and saving the file
        to the text_files directory

        :param item_path: the path to the text file
    """
    def handle_text_file(self, item_path: str) -> None:
        self.send_request(item_path)
        try:
            text_file_content = self.read_response(item_path, is_text_file=True)
        except:
            print(f"Error reading response from: {item_path}")
            return
        
        # if the item path has already been visited, skip it to avoid loops or traps
        if item_path in self.references_with_issues:
            return

        self.text_file_path_list.append(item_path)

        if len(text_file_content) < self.smallest_text_file.get_size(): 
            self.smallest_text_file = FileStats(item_path, len(text_file_content), text_file_content.decode())

        if len(text_file_content) > self.largest_text_file.get_size():
            self.largest_text_file = FileStats(item_path, len(text_file_content), text_file_content.decode())

        self.save_file(item_path, text_file_content, is_text_file=True)


    """
        Handle a non-text file by sending a request to the Gopher server, reading the response, and saving the file
        to the binary_files directory

        :param item_path: the path to the non-text file
    """
    def handle_non_text_file(self, item_path: str) -> None:
        self.send_request(item_path)

        try:
            non_text_file_content = self.read_response(item_path, is_text_file=False)
        except:
            print(f"Error reading response from: {item_path}")
            return

        if item_path in self.references_with_issues:
            return

        self.binary_file_path_list.append(item_path)

        if len(non_text_file_content) < self.smallest_binary_file.get_size():
            self.smallest_binary_file = FileStats(item_path, len(non_text_file_content), non_text_file_content)

        if len(non_text_file_content) > self.largest_binary_file.get_size():
            self.largest_binary_file = FileStats(item_path, len(non_text_file_content), non_text_file_content)

        self.save_file(item_path, non_text_file_content, is_text_file=False)


    """
        Save a file to the text_files or binary_files directory

        :param file_path: the path to the file
        :param content: the content of the file
        :param is_text_file: whether the file is a text file or not
    """
    def save_file(self, file_path: str, content: bytes, is_text_file: bool) -> None:
        # create folder if it doesn't exist
        folder = "text_files" if is_text_file else "binary_files"
        os.makedirs(folder, exist_ok=True)

        # get the file name
        file_name = file_path.split("/")[-1]

        # if the file name is too long, truncate it
        if len(file_name) > GopherClient.MAX_FILENAME_LENGTH:
            file_name = file_name[:GopherClient.MAX_FILENAME_LENGTH]

        # create the file path
        file_path = os.path.join(folder, file_name)

        # write the content to the file
        with open(file_path, "w" if is_text_file else "wb") as file:
            if is_text_file:
                file.write(content.decode())
            else:
                file.write(content)


    """
        Print the results of the Gopher server
    """
    def print_results(self) -> None:
        print("\n----- Gopher Server Analysis Results -----")
        
        # a. The number of Gopher directories on the server
        print(f"\na. Number of Gopher directories: {len(self.directories)}")
        print("List of Gopher directories:")
        for path in self.directories:
            print(f"{path}")
        
        # b. The number and list of all simple text files (full path)
        print(f"\nb. Number of text files: {len(self.text_file_path_list)}")
        print("List of text files:")
        for path in self.text_file_path_list:
            print(f"{path}")
        
        # c. The number and list of all binary files (full path)
        print(f"\nc. Number of binary files: {len(self.binary_file_path_list)}")
        print("List of binary files:")
        for path in self.binary_file_path_list:
            print(f"{path}")
        
        # d. The contents of the smallest text file
        print(f"\nd. Contents of the smallest text file ({self.smallest_text_file.get_path()}): {self.smallest_text_file.get_size()} bytes")
        print(f"{self.smallest_text_file.get_content()}")
        
        # e. The size of the largest text file
        print(f"\ne. Size of the largest text file ({self.largest_text_file.get_path()}): {self.largest_text_file.get_size()} bytes")
        
        # f. The size of the smallest and the largest binary files
        print(f"\nf. Size of the smallest binary file ({self.smallest_binary_file.get_path()}): {self.smallest_binary_file.get_size()} bytes")
        print(f"   Size of the largest binary file ({self.largest_binary_file.get_path()}): {self.largest_binary_file.get_size()} bytes")
        
        # g. The number of unique invalid references (those with an "error" type)
        print(f"\ng. Number of unique invalid references: {len(self.references_with_errors)}")
        print("List of invalid references:")
        for ref in self.references_with_errors:
            print(f"{ref}")
        
        # h. A list of external servers that were referenced
        print("\nh. List of external servers referenced:")
        for host, (port, is_up) in self.external_servers.items():
            status = "up" if is_up else "down"
            print(f"{host}:{port} ({status})")
        
        # i. Any references that have "issues/errors (error type)"
        print("\ni. References with issues/errors:" )
        for ref in self.references_with_issues:
            print(f"{ref}")
        
        print("\n----- End of Analysis -----")


    def run(self):
        root_path = ""
        self.index_server(root_path)


if __name__ == "__main__":
    SERVER_HOST = "comp3310.ddns.net"
    SERVER_PORT = 70
    client = GopherClient(SERVER_HOST, SERVER_PORT)
    client.run()
    client.print_results()
