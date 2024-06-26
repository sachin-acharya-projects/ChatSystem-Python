from curses import wrapper
from cursed import window
from curses.textpad import Textbox
from threading import Thread
from packages import HandleClient, ColoredText
import curses
import inspect
import os
import configparser
import datetime

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


def handleReceivedMessages(
    parent: window.CursedWindow, refresh_param: tuple, window: window.CursedWindow, handleClient: HandleClient
):
    global isFirstMessage
    while True:
        if setCloseConnection():
            break
        incomming: tuple[str, str] = handleClient.getMessage()
        if incomming:
            username, message = incomming
            if isFirstMessage:
                window.clear()
                isFirstMessage = False
            if isSubpadFull(window, len(str(username + message).split("\n"))):
                window.clear()
                parent.refresh(*refresh_param)

            name = username
            date = ""
            if "(" in username:
                name, date = username.split("(")
                date = date.split(")")[0].strip()
            window.addstr("┌──", curses.color_pair(4))
            window.addstr("(")
            window.addstr("%s" % name.strip().title(), curses.color_pair(6))
            window.addstr(")")
            window.addstr(" - Incoming")
            window.addstr("\n| ")
            if date != "":
                date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = datetime.datetime.strftime(date, "%d %B, %Y %I:%M:%S %p")
                window.addstr(f"{date}", curses.color_pair(7))
            else:
                window.addstr(f"System Notification", curses.color_pair(7))
            window.addstr("\n└──$ ")
            if "[CONNECTED" in message:
                date = message.split("-", 1)[1].split("]")[0].strip()
                date = datetime.datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
                date = datetime.datetime.strftime(date, "%d %B, %Y %I:%M:%S %p")
                name_ = message.split("]")[1].strip()
                window.addstr(f"""{name_} connected at {date}\n""")
                message = ""
            for mess in message.split("\n"):
                window.addstr("""{}\n""".format(mess))
            window.addstr("\n")
            parent.refresh(*refresh_param)


def update(n=None):
    global isFirst
    if not n is None:
        isFirst = n
    return isFirst


def handleKeystroke(keystroke: int, window, handleClient):
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

    # Handling Submit
    if keystroke == 10:
        return 7
    if keystroke == 7:
        # Disabling Control-G
        return

    # Handling Line Break
    if keystroke == 529:
        return 14
    if keystroke == 14:
        # Disabling Control-N
        return

    # Handling Delete Character
    if keystroke == 330:
        return 4
    if keystroke == 4:
        return

    if keystroke == "\x1b":  # Don't know what key is this
        handleClient.closeConnection()
        setCloseConnection(True)
        exit(0)

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
    curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)
    curses.init_pair(7, curses.COLOR_MAGENTA, curses.COLOR_BLACK)

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

    attaching_string = "-" * 4
    message = attaching_string + "Logged in as {}".format(USERNAME) + attaching_string
    message_diff = int(((win_one_width - 2) // 2)) + len(message) // 2
    string: str = f"{message:>{message_diff}}"
    newpad.addstr("\n")
    newpad.addstr(string)
    newpad.addstr("\n")
    newpad.addstr(
        f"""
    Following are the shortcut(s) which will come in handy

    KEYS               EVENT
    ───────────────────────────────────────────────────
    ENTER              Send Message
    L_CONTROL+ENTER    INSERT LINE BREAK
    BACKCSPACE         CLEAR THE CHARACTER UNDER CURSOR
    ENTER :EXIT        Exit the current window
    
    PRESS [ENTER] TO CONTINUE
    """.upper(),
        curses.A_BOLD,
    )

    pad.refresh(0, 0, 0, 0, win_one_height, win_one_width)
    window = curses.newwin(8, columns - 2, lines - 8, 1)
    window.border()

    # Creating Subwin - Lines, Columns, Y-Cords, X-Cords
    subwindow = window.subwin(6, columns - 4, lines - 7, 2)
    window.refresh()

    # disable previous character overiding
    box = Textbox(subwindow, insert_mode=True)
    subwindow.addstr("Press [ENTER] to continue")
    subwindow.refresh()
    USERNAME = USERNAME if USERNAME else "Guest"
    handleClient = HandleClient(
        pad,
        newpad,
        (0, 0, 0, 0, win_one_height, win_one_width),
        USERNAME,
        IP=ip_address,
        PORT=port,
    )
    handleClient.connectToserver()
    while True:
        box.edit(lambda x: handleKeystroke(x, subwindow, handleClient))
        text: str = box.gather().strip()
        subwindow.clear()
        subwindow.addstr("Enter your Message")
        subwindow.refresh()
        if text.strip().lower() == ":exit":
            handleClient.closeConnection()
            setCloseConnection(True)
            break
        if text.strip().startswith(":"):
            # Handle explictly as system command
            if ";" in text:
                commands: list[str] = text.split(";")
                for command in commands:
                    if command.lower().startswith("!!"):
                        if not handleClient.sendMessage(command.strip()):
                            newpad.addstr("[CONNECTION CLOSED]", curses.color_pair(5))
                            handleClient.closeConnection()
                            setCloseConnection(True)
                    if command.lower() == ":exit":
                        handleClient.closeConnection()
                        setCloseConnection(True)
                        break
            continue
        global isFirstMessage
        if isFirstMessage:
            newpad.clear()
            Thread(
                target=handleReceivedMessages,
                args=(
                    pad,
                    (0, 0, 0, 0, win_one_height, win_one_width),
                    newpad,
                    handleClient,
                ),
            ).start()
            isFirstMessage = False
            continue
        if not handleClient.sendMessage(text.strip()):
            newpad.addstr("[CONNECTION CLOSED]", curses.color_pair(5))
            handleClient.closeConnection()
            setCloseConnection(True)
        else:
            if not text.startswith("!!"):
                if isSubpadFull(newpad, len(str(USERNAME + text).split("\n"))):
                    newpad.clear()
                    pad.refresh(0, 0, 0, 0, win_one_height, win_one_width)

                newpad.addstr("┌──", curses.color_pair(4))
                newpad.addstr("(")
                newpad.addstr("%s" % USERNAME.strip().title(), curses.color_pair(6))
                newpad.addstr(")")
                newpad.addstr(" - Outgoing")
                newpad.addstr("\n| ")
                date = datetime.datetime.now().strftime("%d %B, %Y %I:%M:%S %p")
                newpad.addstr(f"{date}", curses.color_pair(7))
                newpad.addstr("\n└──$ ")
                # newpad.attron(curses.color_pair(3))
                # newpad.addstr("[Hi{}]\n".format(USERNAME.title()))
                # newpad.attroff(curses.color_pair(3))
                for message in text.split("\n"):
                    newpad.addstr("""{}\n""".format(message.strip()))
                newpad.addstr("\n")
                pad.refresh(0, 0, 0, 0, win_one_height, win_one_width)
        update(True)

    # stdscr.getch()


INFOTEXT: str = """
Informations

If you want to avoid the hassel of providing all these inputs one by one, you can follow the given steps
    
    1. Create a file named configuration.ini in \n\t{}
    2. Edit the file and write following configurations
    
    [Client]
        USERNAME = YOUR_USERNAME
        IP = IP_ADDRESS_OF_SERVER
        PORT = PORT_FOR_SERVER
"""
if __name__ == "__main__":
    config = configparser.ConfigParser()
    config.read("configuration.ini")
    try:
        username = config["Client"]["USERNAME"]
        ip_add = config["Client"]["IP"]
        port = int(config["Client"]["PORT"])
    except KeyError:
        ColoredText.info("What is your Username?")
        username = input(">> ").strip()

        ColoredText.info("\nWhat is the Server's IP Address? (127.0.0.1)")
        ip_add = input(">> ").strip()
        if ip_add == "":
            ip_add = "127.0.0.1"
            print(f"\033[1A>> 127.0.0.1")

        ColoredText.info("\nWhich PORT is Server running on? (8000)")
        port = input(">> ").strip()
        if port == "" or not port.isdigit():
            port = 8000
            print(f"\033[1A>> 8000")

        ColoredText.systemMessage(
            INFOTEXT.format(os.path.dirname(os.path.abspath(__file__)))
        )

        ColoredText.info("\nAre you sure to continue? (E)xit")
        cont = input(">> ").strip()
        if cont == "":
            print(f"\033[1A>> Continue")
        elif cont.lower() == "e":
            exit(0)

    wrapper(lambda x: main(x, ip_address=ip_add, port=int(port), USERNAME=username))
