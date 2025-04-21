import socket
from socket import *
from datetime import datetime

# GopherClient class
# Handles the connection to the gopher server and the parsing of the response
class GopherClient:
    def __init__(self, serverHost, serverPort):
        # Initialize the client with the given server host and port
        self.serverHost = serverHost
        self.serverPort = serverPort
        self.directories = set()
        self.sock = None

    def createSocket(self):
        self.sock = socket(AF_INET, SOCK_STREAM)
        self.sock.settimeout(5)
        self.sock.connect((self.serverHost, self.serverPort))

    def formatDateTime(self):
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def sendClientRequest(self, request):
        print(f"Request: {request}, time: {self.formatDateTime()}")
        request += "\r\n"
        self.createSocket()
        self.sock.sendall(request.encode())
    
    def readReply(self):
        data = b""
        while True:
            try:
                chunk = self.sock.recv(4096)
                if not chunk:
                    break
                data += chunk
            except timeout:
                break

        self.sock.close()

        return data.decode()
    
    def run(self):
        self.sendClientRequest("")
        print(self.readReply())
        
if __name__ == "__main__":
    SERVER_HOST = "comp3310.ddns.net"
    SERVER_PORT = 70

    client = GopherClient(SERVER_HOST, SERVER_PORT)
    client.run()
 
