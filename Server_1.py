from coloredPrint import ColoredText, Fore, Style
from typing import TypedDict
import socket, select, sys, datetime

class ClientType(TypedDict):
    data: bytes
    header: bytes

class ServerHandle:
    HEADER_LENGTH: int = 10
    IP: str = '127.0.0.1'
    PORT: int = 1234
    def __init__(self):
        self.clients: ClientType = {}
        self.messages_chunks: list = []
        self.socket_list: list[socket.socket] = []
    def startServer(self):
        self.server_socket: socket.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        ColoredText.systemMessage(f"""
        Listenning For Connections
        
        [HOST] {self.IP}
        [PORT] {self.PORT}
        """)
        self.server_socket.bind((self.IP, self.PORT))
        self.server_socket.listen()
        self.socket_list = [self.server_socket]
    def incommingMessageHandler(self, client_socket: socket.socket):
        try:
            message_header = client_socket.recv(self.HEADER_LENGTH)
            if not len(message_header):
                return False
            message_length = int(message_header.decode('utf-8').strip())
            return {"header": message_header, "data": client_socket.recv(message_length)}
        except Exception as e:
            ColoredText.errorMessage("Following error occured when trying to retrive message from client\n" + str(e))
            return False
    def startProcessing(self):
        try:
            while True:
                read_sockets, _, exception_sockets = select.select(self.socket_list, [], self.socket_list)
                
                for notified_socket in read_sockets:
                    print("Connection", notified_socket == self.server_socket)
                    if notified_socket == self.server_socket:
                        accepted_server = self.server_socket.accept()
                        client_socket: socket.socket = accepted_server[0]
                        client_address: list = accepted_server[1]
                        user: dict = self.incommingMessageHandler(client_socket)
                        if not user:
                            continue
                        self.socket_list.append(client_socket)
                        self.clients[client_socket] = user
                        decoded_user = user['data'].decode('utf-8')
                        ColoredText.info(f"[NEW CONNECTION] {client_address[0]}:{client_address[1]} {'':<{8}} - {decoded_user}")
                        date: datetime.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        msg: bytes = "{}\n[CONNECTED on {}] {}".format(Fore.LIGHTYELLOW_EX, date, decoded_user).encode('utf-8')
                        msg_header = f"{len(msg):<{self.HEADER_LENGTH}}".encode('utf-8')
                        
                        for message_chunk in self.messages_chunks:
                            client_socket.send(message_chunk)
                        for client_sock in self.clients:
                            if client_sock != notified_socket:
                                client_sock.send(user['header'] + user['data'] + msg_header + msg)
                        self.messages_chunks.append(user['header'] + user['data'] + msg_header + msg)
                    else:
                        message: dict = self.incommingMessageHandler(notified_socket)
                        if not message:
                            ColoredText.info("[DISCONNECTED] {}:{}".format(self.clients[notified_socket]['data'].decode('utf-8'), self.clients[notified_socket]['header'].decode('utf-8')))
                            self.socket_list.remove(notified_socket)
                            del self.clients[notified_socket]
                            continue
                        if message['data'] == b"!!exit":
                            self.server_socket.close()
                            sys.exit(0)
                        
                        user = self.clients[notified_socket]
                        
                        ColoredText.conversation("[MESSAGE RECEIVED] {}:{} - {}".format(user['data'].decode(), user['header'].decode(), message['data'].decode('utf-8')))
                        
                        for client_socket in self.clients:
                            if client_socket != notified_socket:
                                date: datetime.datetime = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                                msg_header = f"{len(message['data']):<{self.HEADER_LENGTH}}".encode('utf-8')
                                new_username: bytes = str(user['data'].decode('utf-8') + " (" + date + ")").encode('utf-8')
                                new_header: bytes = f"{len(new_username):<{self.HEADER_LENGTH}}".encode('utf-8')
                                recv = new_header + new_username + msg_header + message['data']
                                client_socket.send(recv)
                                self.messages_chunks.append(recv)
        
                        for notified_socket in exception_sockets:
                            self.socket_list.remove(notified_socket)
                            del self.clients[notified_socket]
                            continue
        except Exception as e:
            ColoredText.errorMessage(str(e))
        finally:
            self.server_socket.close()
            sys.exit(0)
            
if __name__ == '__main__':
    server = ServerHandle()
    server.startServer()
    server.startProcessing()