from curses import wrapper
from curses.textpad import Textbox
import curses, os

# Global Variables
isFirst = True
"""
    for i in range(100000):
        newpad.addstr(str(i) + "\n")
        pad.refresh(0, 0, 0, 0, win_one_height, win_one_width)
"""
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

def main(stdscr: curses.initscr, USERNAME: str = "Guest"):
    stdscr.clear()
    stdscr.nodelay(True)
    
    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(4, curses.COLOR_WHITE, curses.COLOR_BLACK)
    
    # size = os.get_terminal_size()
    lines, columns = stdscr.getmaxyx()
    win_one_height, win_one_width = lines - 9, columns - 1
    pad = curses.newpad(win_one_height, win_one_width)
    pad.border()
    newpad = pad.subpad(win_one_height - 2, win_one_width - 2, 1, 1)
    newpad.scrollok(True)
    
    # Display initial Context
    message = "WELCOME TO CHATBOX BY SOCKET"
    message_diff = int(((win_one_width - 2) // 2)) + len(message) // 2
    string: str = f"{message:>{message_diff}}"
    
    newpad.attron(curses.color_pair(3))
    newpad.addstr("\n")
    newpad.addstr(string)
    newpad.addstr("\n")
    newpad.attroff(curses.color_pair(3))
    
    newpad.addstr(f"""
    Following are shortcut which will come in handy
    
    [ENTER]             Send Message
    [L_CONTROL+ENTER]   INSERT LINE BREAK
    [BACKCSPACE]        CLEAR THE CHARACTER UNDER CURSUR
    [ENTER :EXIT]       Exit the current window
    
    [USERNAME] {USERNAME}
    """.upper(), curses.A_BOLD)
    
    pad.refresh(0, 0, 0, 0, win_one_height, win_one_width)
    window = curses.newwin(8, columns - 2, lines - 8, 1)
    window.border()
    
    # Creating Subwin - Lines, Columns, Y-Cords, X-Cords
    subwindow = window.subwin(6, columns - 4, lines - 7, 2)
    window.refresh()
    
    box = Textbox(subwindow, insert_mode=True) # disable previous character overiding
    subwindow.addstr("Enter your Message")
    subwindow.refresh()
        
    while True:
        box.edit(lambda x: handleKeystroke(x, subwindow))
        text: str = box.gather().strip()
        if text.strip().lower() == ':exit':
            break
        subwindow.clear()
        subwindow.addstr("Enter your Message")
        subwindow.refresh()
        update(True)
    # stdscr.getch()
wrapper(lambda x: main(x, "Sachin Acharya"))