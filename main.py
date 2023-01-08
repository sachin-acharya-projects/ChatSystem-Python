from curses import wrapper
from curses.textpad import Textbox
from threading import Thread
from clientHandle import ClientHandle
import curses, inspect, os
import configparser

# Global Variables
isFirst = True
closeConnection = False
isFirstMessage = True
def whichIsParent():
    return inspect.stack()[2][3]
def print_stuff(*array):
    print("From " + whichIsParent(), " ".join(array))
def setCloseConnection(reset=False):
    global closeConnection
    if reset:
        closeConnection = True
    return closeConnection
def isSubpadFull(subpad, len_: int = 0):
    height, _ = subpad.getmaxyx()
    cursor_y, _ = subpad.getyx()
    return (cursor_y + len_) > height - 2
def handleReceivedMessages(parent, refresh_param: tuple, window, clientHandle: ClientHandle):
    global isFirstMessage
    while True:
        if setCloseConnection():
            break
        incomming: tuple(str, str) = clientHandle.getMessage()
        if incomming:
            username, message = incomming
            if isFirstMessage:
                window.clear()
                isFirstMessage = False
            if isSubpadFull(window, len(str(username + message).split("\n"))):
                window.clear()
                parent.refresh(*refresh_param)
            window.attron(curses.color_pair(3))
            window.addstr("[{}]\n".format(username.title()))
            window.attroff(curses.color_pair(3))
            for mess in message.split("\n"):
                window.addstr("""  {}\n""".format(mess))
            window.addstr("\n")
            parent.refresh(*refresh_param)
def update(n=None):
    global isFirst
    if not n is None:
        isFirst = n
    return isFirst
def handleKeystroke(keystroke: int, window):
    "Handle Keystroke -- Kinda like Keypress Event"
    ###############################################
    # KEYSTROKE CHART                             #
    # ENTER 10                                    #
    # Control-G 10 (Submit Value)                 #
    # Control-N 14 (Line-Break)                   #
    # Control-ENTER 529                           #
    # Control-H 8 (Delete Backward)               #
    # Control-L 12 (Refresh Screen)               #
    # Delete 330                                  #
    # Control-D 4 (Delete Character Under Curser) #
    ###############################################
    if keystroke == 10:
        return 7
    if keystroke == 7:
        # Disabling Control-G
        return
    if keystroke == 529:
        return 14
    if keystroke == 14:
        # Disabling Control-N
        return
    if keystroke == 330:
        return 4
    if keystroke == 4:
        return
    if keystroke == '\x1b':
        exit()
    if update():
        window.clear()
        # global isFirst
        update(False)
    return keystroke

def main(stdscr: curses.initscr, ip_address: str, port: int, USERNAME: str):
    stdscr.clear()
    stdscr.nodelay(True)

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)

    # size = os.get_terminal_size()
    lines, columns = stdscr.getmaxyx()
    win_one_height, win_one_width = lines - 9, columns - 1
    pad = curses.newpad(win_one_height, win_one_width)
    pad.border()
    newpad = pad.subpad(win_one_height - 2, win_one_width - 2, 1, 1)
    newpad.scrollok(True)

    message = "WELCOME TO CHATBOX BY SOCKET"
    message_diff = int(((win_one_width - 2) // 2)) + len(message) // 2
    string: str = f"{message:>{message_diff}}"

    newpad.attron(curses.color_pair(3))
    newpad.addstr("\n")
    newpad.addstr(string)
    newpad.addstr("\n")
    newpad.attroff(curses.color_pair(3))

    attaching_string = '-' * 4
    message = attaching_string + "Logged in as {}".format(USERNAME) + attaching_string
    message_diff = int(((win_one_width - 2) // 2)) + len(message) // 2
    string: str = f"{message:>{message_diff}}"
    newpad.addstr("\n")
    newpad.addstr(string)
    newpad.addstr("\n")
    newpad.addstr(f"""
    Following are the shortcut(s) which will come in handy

    KEYS               EVENT
    ───────────────────────────────────────────────────
    ENTER              Send Message
    L_CONTROL+ENTER    INSERT LINE BREAK
    BACKCSPACE         CLEAR THE CHARACTER UNDER CURSOR
    ENTER :EXIT        Exit the current window
    
    PRESS [ENTER] TO CONTINUE   
    """.upper(), curses.A_BOLD)

    pad.refresh(0, 0, 0, 0, win_one_height, win_one_width)
    window = curses.newwin(8, columns - 2, lines - 8, 1)
    window.border()

    # Creating Subwin - Lines, Columns, Y-Cords, X-Cords
    subwindow = window.subwin(6, columns - 4, lines - 7, 2)
    window.refresh()

    box = Textbox(subwindow, insert_mode=True) # disable previous character overiding
    subwindow.addstr("Press [ENTER] to continue")
    subwindow.refresh()
    USERNAME = USERNAME if USERNAME else "Guest"
    clientHandle = ClientHandle(pad, newpad, (0, 0, 0, 0, win_one_height, win_one_width),USERNAME, ip_address, port)
    clientHandle.connectToserver()
    while True:
        box.edit(lambda x: handleKeystroke(x, subwindow))
        text: str = box.gather().strip()
        subwindow.clear()
        subwindow.addstr("Enter your Message")
        subwindow.refresh()
        if text.strip().lower() == ':exit':
            clientHandle.closeConnection()
            setCloseConnection(True)
            break
        if text.strip().startswith(":"):
            # Handle explictly as system command
            if ";" in text:
                commands: list[str] = text.split(";")
                for command in commands:
                    if command.lower().startswith("!!"):
                        if not clientHandle.sendMessage(command.strip()):
                            newpad.addstr("[CONNECTION CLOSED]", curses.color_pair(5))
                            clientHandle.closeConnection()
                            setCloseConnection(True)
                    if command.lower() == ':exit':
                        clientHandle.closeConnection()
                        setCloseConnection(True)
                        break
            continue
        global isFirstMessage
        if isFirstMessage:
            newpad.clear()
            Thread(target=handleReceivedMessages, args=(pad, (0, 0, 0, 0, win_one_height, win_one_width),newpad, clientHandle)).start()
            isFirstMessage = False
            continue
        if not clientHandle.sendMessage(text.strip()):
            newpad.addstr("[CONNECTION CLOSED]", curses.color_pair(5))
            clientHandle.closeConnection()
            setCloseConnection(True)
        else:
            if not text.startswith("!!"):
                if isSubpadFull(newpad, len(str(USERNAME + text).split("\n"))):
                    newpad.clear()
                    pad.refresh(0, 0, 0, 0, win_one_height, win_one_width)
                    
                newpad.attron(curses.color_pair(3))
                newpad.addstr("[{}]\n".format(USERNAME.title()))
                newpad.attroff(curses.color_pair(3))
                for message in text.split("\n"):
                    newpad.addstr("""  {}\n""".format(message.strip()))
                newpad.addstr("\n")
                pad.refresh(0, 0, 0, 0, win_one_height, win_one_width)
        update(True)
    # stdscr.getch()
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read('configuration.ini')
    try:
        username = config['Client']['USERNAME']
        ip_add = config['Client']['IP']
        port = int(config['Client']['PORT'])
    except KeyError:
        username = input("What is your username? ")
        ip_add = input("What is the IP ADDRESS of server(127.0.0.1)\n")
        ip_add = ip_add if ip_add else '127.0.0.1'
        port = input("Which PORT is server running?(8888) ")
        port = port if port else 8888
        
        print("[information] If you want to avoid the hassel of providing all this parameter one by one")
        print("you can following following method")
        print("""Store [CONFIGURATION] Locally
              1. Create a File named configuration.ini in {}
              2. Edit the file (.ini) file and write as following
              [Client]
                USERNAME = YOUR_USERNAME
                IP = IP_ADDRESS_OF_SERVER
                PORT = PORT_ON_WHICH_SERVER_IS_RUNNING
        """.format(os.path.dirname(os.path.abspath(__file__))))
    wrapper(lambda x: main(x, ip_add, port, username))