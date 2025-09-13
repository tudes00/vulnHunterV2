import sys
import subprocess
from questionary import Style
from pyfiglet import Figlet
from rich import print 
from rich.text import Text

from rich.traceback import install
install(show_locals=True)

custom_style = Style([
    ('qmark', 'fg:#FF4B4B bold'),        
    ('question', 'fg:#FFFFFF bold'),     
    ('answer', 'fg:#FF4B4B bold'),       
    ('pointer', 'fg:#FF4B4B bold'),      
    ('highlighted', 'fg:#FF4B4B bold'),  
    ('selected', 'fg:#FF4B4B'),          
    ('separator', 'fg:#CCCCCC'),         
    ('instruction', 'fg:#AAAAAA italic'),
    ('text', 'fg:#FFFFFF'),              
    ('disabled', 'fg:#555555 italic')    
])

version = "2.0.0"

defaultWordlistDirFinder = "utils/wordlist/testSmall.txt"
USER_AGENT = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"

def getOs():
    return sys.platform

def clearScreen():
    subprocess.call("clear", shell=True)
    displayLogo()

def exit():
    print("[bold red]Exiting...[/bold red]")
    sys.exit()

f = Figlet(font='slant')
def displayLogo():
    vulnAscii = f.renderText("Vuln").splitlines()
    HunterAscii = f.renderText("Hunter").splitlines()

    for line_s, line_b in zip(vulnAscii, HunterAscii):
        left = Text(line_s, style="bold red")
        right = Text(line_b, style="bold white")
        print(left.append(right))

    print(f"          made by Tudes - Version [bold white]{version}[/bold white]")
    print(f"[bold red]━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━[/bold red]")

