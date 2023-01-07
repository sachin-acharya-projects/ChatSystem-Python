from colorama import Fore, Style, init; init(autoreset=True)
class ColoredText:
    # Print Directly
    def info(text):
        print(f"{Fore.LIGHTCYAN_EX}{text}")
    def systemMessage(text):
        print(f"{Fore.CYAN}{text}")
    def errorMessage(text):
        print(f"{Fore.LIGHTRED_EX}{text}")
    def conversation(text):
        print(f"{Fore.LIGHTWHITE_EX}{text}")
    
    # Return colored
    def t_info(text):
        return(f"{Fore.LIGHTCYAN_EX}{text}")
    def t_systemMessage(text):
        return(f"{Fore.LIGHTCYAN_EX}{text}")
    def t_errorMessage(text):
        return(f"{Fore.LIGHTRED_EX}{text}")
    def t_conversation(text):
        return(f"{Fore.LIGHTWHITE_EX}{text}")