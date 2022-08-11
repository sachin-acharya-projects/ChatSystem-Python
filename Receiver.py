from coloredPrint import ColoredText, Fore
import socket, errno, sys

HEADER_LENGTH = 10
IP = '127.0.0.1'
PORT = 1234

ColoredText.info("What is your Username?")
uname = '[VIEWER] ' + input(">> ")

client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
print("\n")
while True:
    try:
        client_socket.connect((IP, PORT))
        ColoredText.info("[CONNECTION ESTABLISHED] Successfully\n")
        break
    except ConnectionRefusedError:
        print(f"{Fore.LIGHTCYAN_EX}[SERVER OFFLINE] Waiting for connection\r", end="")
        continue
client_socket.setblocking(False)

username = uname.encode('utf-8')
username_header = f"{len(username):<{HEADER_LENGTH}}".encode('utf-8')
client_socket.send(username_header + username)

while True:
    try:
        while True:
            username_header = client_socket.recv(HEADER_LENGTH)
            if not len(username_header):
                ColoredText.errorMessage("Connection closed by the server")
                sys.exit()
            username_length = int(username_header.decode('utf-8').strip())
            username = client_socket.recv(username_length).decode('utf-8')
            
            message_header = client_socket.recv(HEADER_LENGTH)
            message_length = int(message_header.decode('utf-8').strip())
            message = client_socket.recv(message_length).decode('utf-8')
            
            ColoredText.conversation(f"{message}")
    except IOError as e:
        if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
            ColoredText.errorMessage("Reading error: {}".format(str(e)))
            sys.exit()
        continue
    except Exception as e:
        ColoredText.errorMessage(f"{e}")