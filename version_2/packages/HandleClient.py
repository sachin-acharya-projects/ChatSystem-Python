from cursed.window import CursedWindow  # I know
import socket
import curses
import errno  # os, sys

__all__ = ["HandleClient"]


class HandleClient:
    HEADER_LENGTH: int = 10
    PORT: int = 1234

    def __init__(
        self, parent, window, refresh_param, username: str, PORT: int, IP: str = None
    ):
        # only for auto-complete (type hint)
        self.window: CursedWindow = window
        self.uname: str = username
        self.parent: CursedWindow = parent
        self.refresh_param: tuple[int] = refresh_param
        self.IP: str = IP if IP else "127.0.0.1"
        self.PORT: str = PORT if PORT else 8888

    def connectToserver(self):
        self.client_socket: socket.socket = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )
        isInformed = False
        while True:
            try:
                self.client_socket.connect((self.IP, self.PORT))
                self.window.attron(curses.color_pair(3))
                self.window.addstr("[CONNECTION ESTABLISHED]\n")
                self.window.attroff(curses.color_pair(3))
                self.parent.refresh(*self.refresh_param)
                break
            except ConnectionRefusedError:
                if not isInformed:
                    self.window.attron(curses.color_pair(5))
                    self.window.addstr("[SERVER OFFLINE] WAITING FOR CONNECTION")
                    self.window.attroff(curses.color_pair(5))
                    self.parent.refresh(*self.refresh_param)
                    isInformed = True
                continue
        self.client_socket.setblocking(False)
        self.username: bytes = self.uname.encode("utf-8")
        self.username_header: bytes = (
            f"{len(self.username):<{self.HEADER_LENGTH}}".encode("utf-8")
        )
        self.client_socket.send(self.username_header + self.username)

    def sendMessage(self, message: str):
        message: bytes = message.encode("utf-8")
        message_header: bytes = f"{len(message):<{self.HEADER_LENGTH}}".encode("utf-8")
        try:
            self.client_socket.send(message_header + message)
            return True
        except Exception:
            return False

    def getMessage(self):
        try:
            username_header: bytes = self.client_socket.recv(self.HEADER_LENGTH)
            if not len(username_header):
                self.window.attron(curses.color_pair(5))
                self.window.addnstr("[CONNECTION CLOSED]")
                self.window.attroff(curses.color_pair(5))
                self.parent.refresh(*self.refresh_param)
                return False
            username_length: int = int(username_header.decode("utf-8").strip())
            username: str = self.client_socket.recv(username_length).decode("utf-8")
            message_header: bytes = self.client_socket.recv(self.HEADER_LENGTH)
            message_length: int = int(message_header.decode("utf-8").strip())
            message: str = self.client_socket.recv(message_length).decode("utf-8")
            return username, message
        except IOError as e:
            if e.errno != errno.EAGAIN and e.errno != errno.EWOULDBLOCK:
                return False
        except Exception as e:
            return False

    def closeConnection(self):
        self.client_socket.close()
