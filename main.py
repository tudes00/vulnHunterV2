from utils.utils import custom_style, getOs, clearScreen, exit
from utils.modulesIndex import nmap, dirFinder, backup, settings

from rich import print
import questionary
import sys

from rich.traceback import install

install(show_locals=True)



def display_tools():
    clearScreen()
    task = questionary.select(
        "What would you like to do?",
        choices=["nmap", "directory finder", "backup finder", "settings", "exit"],
        style=custom_style).ask()
    handle_task(task)


def handle_task(task):
    if task == "exit" or task is None:
        exit()
    elif task == "nmap":
        nmap()
    elif task == "directory finder":
        dirFinder()
    elif task == "backup finder":
        backup()
    elif task == "settings":
        settings()
    else:
        print("[bold red]Invalid option selected![/bold red]")
        questionary.press_any_key_to_continue().ask()
        clearScreen()
        display_tools()


def main():
    try:
        clearScreen()

        if getOs() != "linux":
            print(
                f"[bold red]Your OS is not fully supported. Contact me to help me improve this project! [/bold red]"
            )

        display_tools()

    except KeyboardInterrupt:
        exit()


if __name__ == "__main__":
    main()
