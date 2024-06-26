from packages import *
import socket, select, sys, datetime

# PUBLIC_IP: str = whatsmyip() ; PUBLIC_IP: str = PUBLIC_IP if PUBLIC_IP else IP
PUBLIC_IP = IP  # can also use 0.0.0.0

server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

ColoredText.systemMessage(
    f"""
    Listenning For Connections
    
    HOST: {PUBLIC_IP} (LOCALLY)
    PORT: {PORT}
"""
)
server_socket.bind((IP, PORT))
server_socket.listen()

socket_list = [server_socket]

clients = {}


def receive_message(client_socket):
    try:
        message_header = client_socket.recv(HEADER_LENGTH)
        if not len(message_header):
            return False
        message_length = int(message_header.decode("utf-8").strip())
        return {"header": message_header, "data": client_socket.recv(message_length)}
    except:
        return False


messages_chunks = []
try:
    while True:
        read_sockets, _, exception_sockets = select.select(socket_list, [], socket_list)

        for notified_socket in read_sockets:
            if notified_socket == server_socket:
                client_socket, client_address = server_socket.accept()
                user = receive_message(client_socket)
                if not user:
                    continue
                socket_list.append(client_socket)
                clients[client_socket] = user
                decoded_user = user["data"].decode("utf-8")
                ColoredText.info(
                    f"[NEW CONNECTION] {client_address[0]}:{client_address[1]} {'':<{8}} - {decoded_user}"
                )
                date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                msg = "[CONNECTED - {}] {}\n".format(date, decoded_user)
                msg = msg.encode("utf-8")
                msg_header = f"{len(msg):<{HEADER_LENGTH}}".encode("utf-8")
                for message_chunk in messages_chunks:
                    client_socket.send(message_chunk)
                for client_sock in clients:
                    if client_sock != notified_socket:
                        client_sock.send(
                            user["header"] + user["data"] + msg_header + msg
                        )
                messages_chunks.append(user["header"] + user["data"] + msg_header + msg)
            else:
                message = receive_message(notified_socket)
                if not message:
                    ColoredText.info(
                        "[DISCONNECTED] {}:{}".format(
                            clients[notified_socket]["data"].decode("utf-8"),
                            clients[notified_socket]["header"].decode("utf-8"),
                        )
                    )
                    for sock in clients:
                        if sock != notified_socket:
                            date: str = datetime.datetime.now().strftime(
                                "%Y-%m-%d %H:%M:%S"
                            )
                            user = clients[notified_socket]["data"]
                            user_header = f"{len(user):<{HEADER_LENGTH}}".encode(
                                "utf-8"
                            )
                            message = "[DISCONNECTED - {}] {}".format(
                                date, clients[notified_socket]["data"].decode("utf-8")
                            ).encode("utf-8")
                            msg_header = f"{len(message):<{HEADER_LENGTH}}".encode(
                                "utf-8"
                            )
                            sock.send(user_header + user + msg_header + message)
                    socket_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
                if message["data"] == b"!!clear":
                    messages_chunks.clear()
                if message["data"] == b"!!exit":
                    server_socket.close()
                    sys.exit()
                user = clients[notified_socket]
                ColoredText.conversation(
                    "[MESSAGE RECEIVED] {}:{} - {}".format(
                        user["data"].decode("utf-8"),
                        user["header"].decode("utf-8"),
                        message["data"].decode("utf-8"),
                    )
                )
                for client_socket in clients:
                    if client_socket != notified_socket:
                        date: str = datetime.datetime.now().strftime(
                            "%Y-%m-%d %H:%M:%S"
                        )
                        msg_header = f"{len(message['data']):<{HEADER_LENGTH}}".encode(
                            "utf-8"
                        )
                        new_username: bytes = str(
                            user["data"].decode("utf-8") + " (" + date + ")"
                        ).encode("utf-8")
                        new_header: bytes = (
                            f"{len(new_username):<{HEADER_LENGTH}}".encode("utf-8")
                        )
                        recv = new_header + new_username + msg_header + message["data"]
                        client_socket.send(recv)
                        messages_chunks.append(recv)
                for notified_socket in exception_sockets:
                    socket_list.remove(notified_socket)
                    del clients[notified_socket]
                    continue
except KeyboardInterrupt:
    server_socket.close()
    sys.exit()
