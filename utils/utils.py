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


USER_AGENTS = [
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",
    "Mozilla/5.0 (X11; Linux x86_64) Gecko/20100101 Firefox/126.0",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:40.0) Gecko/20100101 Firefox/40.1",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15",
    "Mozilla/5.0 (Linux; Android 10; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.106 Mobile Safari/537.36",
    "Mozilla/5.0 (iPhone; CPU iPhone OS 13_5_1 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.1 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2228.0 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:52.0) Gecko/20100101 Firefox/52.0",
    "Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_11_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36",
    "Mozilla/5.0 (Linux; U; Android 4.2.2; en-us; GT-I9505 Build/JDQ39) AppleWebKit/534.30 (KHTML, like Gecko) Version/4.0 Mobile Safari/534.30",
    "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)",
    "Mozilla/5.0 (compatible; Bingbot/2.0; +http://www.bing.com/bingbot.htm)",
]

defaultWordlistDirFinder = "utils/wordlist/small.txt"
defaultWordlistDirFinderRecursive = "utils/wordlist/defaultDirFinderSmall.txt"

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


