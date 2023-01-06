from curses import wrapper
from curses.textpad import Textbox #, rectangle
from longest_text import set_text
import curses, os

isFirst = True

current_text = ""
scroll_pos = 0
doReload: bool = False

def clear_win(*window, indexs=None):
    "Clear Window and add border -- unless passed as indexs[]"
    for index, win in enumerate(window):
        win.clear()
        if not index in indexs:
            win.border()
def print_out(window: curses.window, text: str, width: int, coord: list[int, int]):
    """
    Print Text with line-break
    """
    message_difference = (width // 2) - len(text)
    message_list = []
    if message_difference == 0:
        message_list.append(text[:len(text) - 1])
        message_list.append(text[-1])
    elif message_difference < 0:
        message_list.append(text[:len(text) + message_difference - 1])
        message_list.append(text[message_difference - 1])
    else:
        message_list.append(text)
    for index, message in enumerate(message_list):
        window.addstr(coord[0] + index, coord[1], f"{message}")
        window.refresh()

# def scroll_win(window, count = 1):
#     for _ in range(count):
#         window.scroll()

def scroll_up():
    global scroll_pos
    scroll_pos = max(0, scroll_pos - 1)

def scroll_down(messages, window):
    global scroll_pos
    scroll_pos = min(len(messages) - window.getmaxyx()[0], scroll_pos + 1)

def setSingleString(window, texts: str, row_column: list[list[int]]=None):
    list_string = texts.split("<sachin:splitter>")
    
    window.attron(curses.color_pair(3))
    window.addstr(*row_column[0], str(list_string[0]))
    window.attroff(curses.color_pair(3))
    window.refresh()
    window.addstr(*row_column[1], str(list_string[1]))
    window.refresh()
    window.addstr(*row_column[2], f""" {str(list_string[2])}""")
    window.refresh()

def getDoReload(set_true: bool = False, reset: bool = False):
    global doReload
    if set_true:
        doReload = True
    if reset:
        doReload = False
    return doReload

def printMainWindow(window: curses.newwin, width: int, text: str, coord: list[int] = None):
    # row = -1000
    row = coord[0]
    messages: list[str] = []
    for message in text.split("\n"):
        for index in range(0, len(message), width):
            messages.append(message[index:index + width])
    os.system("cls")
    
    getDoReload(reset=True)
    listing_index: list[list[int]] = []
    message_x: str = ""
    for index, message in enumerate(messages):
        # if getDoReload() and len(listing_index) >= 3:
        #     clear_win(window, indexs=[0])
        #     setSingleString(window, message_x, listing_index)
        #     listing_index.clear()
        #     message_x = ""
        #     getDoReload(reset=True)
        if message.startswith("u:"):
            message = message.lstrip("u:").title()
            try:
                window.attron(curses.color_pair(3))
                window.addstr(row, coord[1], str(message))
                window.attroff(curses.color_pair(3))
            except curses.error:
                row = coord[0] + 1
                getDoReload(set_true=True)
            finally:
                listing_index.append([row, coord[1]])
                message_x += f"{message}<sachin:splitter>"
                row += 1
            continue
            
        if message.startswith("space:"):
            try:
                window.addstr(row, coord[1], "\n")
            except curses.error:
                row = coord[0] + 1
                getDoReload(set_true=True)
            finally:
                listing_index.append([row, coord[1]])
                message_x += "\n<sachin:splitter>"
                row += 1
            continue
            
        try:
            window.addstr(row, coord[1], f""" {str(message)}""")
        except curses.error:
            row = coord[0] + 1
            getDoReload(set_true=True)
        finally:
            listing_index.append([row, coord[1]])
            # message_x += f""" {str(message)}<sachin:splitter>"""
            message_x += f""" {str(message)}"""
            row += 1
        window.refresh()
def update(n=None):
    global isFirst
    if not n is None:
        isFirst = n
    return isFirst
def handle_keystroke(keystroke, window):
    "Handle Keystroke -- Kinda like Keypress Event"
    
    # Capturing Keystroke in file to analyze
    # with open("file.txt", "a+") as f:
    #     f.write(f"{keystroke}\n")
    
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
    # with open("log.txt", 'a') as f:
    #     f.write(f"{isFirst}")
    if update():
        clear_win(window, indexs=[0])
        # global isFirst
        update(False)
    return keystroke
def main(stdscr: curses.initscr):
    size = os.get_terminal_size() # Lines - 58 Columns - 91

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
    curses.init_pair(3, curses.COLOR_CYAN, curses.COLOR_BLACK)
    
    stdscr.clear()
    
    # Creating Newwin - Lines, Columns, Y-Cords, X-Cords
    win_one_height, win_one_width = size.lines - 9, size.columns - 2
    window_one = curses.newwin(win_one_height, win_one_width, 1, 1)
    window_one.border()
    height, width = window_one.getmaxyx()
    # window_one_subwin = window_one.derwin(win_one_height, win_one_width)
    # window_one_subwin = window_one.subpad(win_one_height - 2, win_one_width - 2)
    window_one_subwin = window_one.derwin(win_one_height - height + 1, win_one_width - width + 1) # Don't know why this weird calculation. it just works
    # window_one_subwin.setscrreg(0, 13)
    window_one_subwin.scrollok(True)
    # window_one_subwin.bkgd(' ', curses.color_pair(1))

    # message = "Hello, My name is Sachin Acharya "
    # # Coordination is kinda messed up
    print_out(window_one, "Welcome to Chatbox v2 with Socket", win_one_width, (1, 2))
    # window_one.addstr(0, 0, "Welcome to Chatbox with Socket")
    window_one.refresh()

    window_two = curses.newwin(8, size.columns - 2, size.lines - 8, 1)
    # window_two.bkgd(' ', curses.color_pair(2))
    window_two.border()

    # Creating Subwin - Lines, Columns, Y-Cords, X-Cords
    win_two_subwin = window_two.subwin(6, size.columns - 4, size.lines - 7, 2)
    window_two.refresh()

    box = Textbox(win_two_subwin, insert_mode=True) # disable previous character overiding
    win_two_subwin.addstr("Enter your Message")
    win_two_subwin.refresh()
    while True:
        box.edit(lambda x: handle_keystroke(x, win_two_subwin))
        text = box.gather().strip()
        if text.strip() == 'exit':
            break
        clear_win(window_one, win_two_subwin, indexs=[1])
        # window_one.scroll()
        global current_text
        current_text = current_text + "u:[Sachin Acharya]\n" + text + "\n" + "space:\n"
        # print(current_text)
        printMainWindow(window_one_subwin, win_one_width, current_text, (1, 1))
        # window_one.refresh()
        win_two_subwin.addstr("Enter your Message")
        win_two_subwin.refresh()
        update(True)

wrapper(main)

# ReCreate new subpad window 