from curses import wrapper
from curses.textpad import Textbox, rectangle
import curses, os

isFirst = True

def clear_win(*window, indexs=None):
    "Clear Window and add border -- unless passed as indexs[]"
    for index, win in enumerate(window):
        win.clear()
        if not index in indexs:
            win.border()
def print_out(window, text, width, coord):
    """
    Print Text with line-break
    """
    lines, columns = os.get_terminal_size()
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
    with open("log.txt", 'a') as f:
        f.write(f"{isFirst}")
    if update():
        clear_win(window, indexs=[0])
        # global isFirst
        update(False)
    return keystroke
def main(stdscr: curses.initscr):
    size = os.get_terminal_size() # Lines - 58 Columns - 91

    curses.init_pair(1, curses.COLOR_WHITE, curses.COLOR_BLUE)
    curses.init_pair(2, curses.COLOR_WHITE, curses.COLOR_RED)
    
    stdscr.clear()
    
    # Creating Newwin - Lines, Columns, Y-Cords, X-Cords
    win_one_height, win_one_width = size.lines - 9, size.columns - 2
    window_one = curses.newwin(win_one_height, win_one_width, 1, 1)
    # window_one.bkgd(' ', curses.color_pair(1))

    message = "Hello, My name is Sachin Acharya "

    # Coordination is kinda messed up
    print_out(window_one, message, win_one_width, (win_one_height // 2, (win_one_width - len(message)) // 2))
    
    window_one.border()
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
        print_out(window_one, text, win_one_width, (win_one_height // 2, (win_one_width - len(text)) // 2))
        win_two_subwin.addstr("Enter your Message")
        win_two_subwin.refresh()
        update(True)

wrapper(main)
