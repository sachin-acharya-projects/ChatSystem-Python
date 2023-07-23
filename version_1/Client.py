from packages import *
import socket, sys, os

ColoredText.info("What is your Username?")
uname = input(">> ")

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

try:
    while True:
        os.system("cls")
        print(f"{Fore.LIGHTCYAN_EX}\n[{uname}]>> ", end="")
        message = input()
        
        if message:
            if message == "!!logout":
                try:
                    client_socket.close()
                except:
                    pass
                sys.exit()
            message = message.encode('utf-8')
            message_header = f"{len(message):<{HEADER_LENGTH}}".encode('utf-8')
            try:
                client_socket.send(message_header + message)
            except Exception:
                client_socket.close()
                sys.exit()
except KeyboardInterrupt:
    client_socket.close()
    sys.exit()