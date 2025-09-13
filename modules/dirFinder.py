import os
import re
import sys
import datetime
import aiohttp
import asyncio
import ssl
import socket
import random
import time
from rich import print
from rich.panel import Panel
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, TextColumn, BarColumn, TaskProgressColumn, TimeRemainingColumn, TimeElapsedColumn, SpinnerColumn
from rich.live import Live
from rich.layout import Layout
from rich.panel import Panel
from rich.traceback import install
import questionary
from aiohttp import ClientConnectorError, ClientOSError, ServerDisconnectedError, ClientResponseError

install(show_locals=True)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from utils.utils import defaultWordlistDirFinder

console = Console()
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

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

PROXY = [
    "testt zebii la mouche"
]

def dirFinder():
    from main import display_tools
    building = True

    try:
        console.print(Panel.fit("[bold red]Welcome to DirFinder![/bold red]\n", title="DirFinder", subtitle="Directory Scanner"))

        while True:
            target = questionary.text("Enter the target to scan:").ask()
            if target: break
            if target is None:
                display_tools()
                return
            print("[bold red]No target provided. Please enter a target.[/bold red]")

        while True:
            user_input = questionary.text("Wordlist path [leave empty for default]:").ask()
            if user_input is None:
                display_tools()
                return


            base_dir = os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), "../"))
            if user_input:
                wordlist = os.path.abspath(os.path.expanduser(user_input)) if os.path.isabs(user_input) else os.path.join(base_dir, user_input)
            else:
                wordlist = os.path.join(base_dir, defaultWordlistDirFinder)
    

            if os.path.isfile(wordlist):
                print(f"[bold green]Using wordlist:[/bold green] {wordlist}")
                break
            else:
                print(f"[bold red]The file {wordlist} does not exist![/bold red]")

        max_threads = questionary.text("Enter max concurrent requests [default 100]:").ask()
        try:
            max_threads = int(max_threads) if max_threads else 100
        except ValueError:
            max_threads = 100

        timeout = questionary.text("Enter max timeout for requests [default 10]:").ask()
        try:
            timeout = int(timeout) if timeout else 10
        except ValueError:
            timeout = 10

        proxy_input = questionary.text(
            "Proxy (format http://127.0.0.1:8080) [leave empty for none]:"
        ).ask()
        proxy = proxy_input.strip() if proxy_input else None

        console.print(Panel.fit(
            f"Target: [bold yellow]{target}[/bold yellow]\nWordlist: [bold yellow]{wordlist}[/bold yellow]\nMax concurrent requests: [bold yellow]{max_threads}[/bold yellow]\nMax timeout: [bold yellow]{timeout}[/bold yellow]\nProxy: [bold yellow]{proxy}[/bold yellow]",
            title="Scan Summary", border_style="bold red"
        ))

        confirm = questionary.confirm("Start scan with the above settings?").ask()
        if not confirm:
            print("[bold red]Scan cancelled.[/bold red]")
            display_tools()
            return

        building = False
        asyncio.run(start(target, wordlist, max_threads, aiohttp.ClientTimeout(total=timeout), proxy))

    except KeyboardInterrupt:
        if building:
            print("\n[bold red]Interrupted by user.[/bold red]")
            display_tools()






async def start(target, wordlistPath, max_threads, timeout, proxy):
    now = datetime.datetime.now()
    console.print(Panel.fit(
        f"[bold cyan] Starting DirFinder scan[/bold cyan]\n\n"
        f"[bold]Date:[/bold] [yellow]{now.strftime('%d/%m/%Y %H:%M:%S')}[/yellow]\n"
        f"[bold]Target:[/bold] [magenta]{target}[/magenta]\n"
        f"[bold]Wordlist:[/bold] [green]{wordlistPath}[/green]",
        title="[bold red]Scan in progress[/bold red]", border_style="bold red"
    ))

    start_time = datetime.datetime.now()
    conn = aiohttp.TCPConnector(limit=max_threads*2, family=0, ssl=False)

    async with aiohttp.ClientSession(connector=conn, timeout=timeout) as session:
        alive, validUrl = await ping(session, target, timeout, proxy)
        if not alive:
            console.print(Panel.fit("[bold red]❌ Host seems down[/bold red]", title="[bold red]Result[/bold red]"))
            return

        console.print(f"[bold green]✅ Host is up![/bold green] URL used: [cyan]{validUrl}[/cyan]")

        with open(wordlistPath, "r", encoding="utf-8") as f:
            words = [w.strip().lstrip("/") for w in f if w.strip()]
        random.shuffle(words)

        table = Table(title="DirFinder Results")
        table.add_column("URL", style="cyan")
        table.add_column("Status", style="magenta")
        table.add_column("Redirect", style="yellow")

        hits = 0
        semaphore = asyncio.Semaphore(max_threads)

        async def fetch_with_retries(word, session, validUrl, proxy, semaphore):
            url = f"{validUrl}/{word}"
            max_attempts = 10
            for attempt in range(max_attempts):
                async with semaphore:
                    await asyncio.sleep(random.uniform(0.05, 0.25))
                    headers = {"User-Agent": random.choice(USER_AGENTS)}
                    try:
                        url, status, location, err = await fetch(session, word, validUrl, proxy, headers)
                    except Exception as e:
                        status, location, err = 0, None, e
                if status == 429 or isinstance(err, (ClientConnectorError, ClientOSError, ServerDisconnectedError, ClientResponseError)):
                    wait_time = (5 ** attempt) + random.uniform(0, 2)
                    if attempt == max_attempts - 1:
                        print(f"[bold red]🚨 Error for url {url} after {max_attempts} attempts: {err}[/bold red]")
                    await asyncio.sleep(wait_time)
                else:
                    return url, status, location, err, word
            return url, status, location, err, word 

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TaskProgressColumn(),
            TimeElapsedColumn(),
            TextColumn("[bold blue]{task.completed}[/bold blue]/[bold yellow]{task.total}[/bold yellow] words")
        )

        with progress:
            task1 = progress.add_task("Scanning...", total=len(words))

            coros = [fetch_with_retries(w, session, validUrl, proxy, semaphore) for w in words]
            for fut in asyncio.as_completed(coros):
                url, status, location, err, word = await fut
                progress.update(task1, advance=1)

                if isinstance(status, Exception) or status == 404:
                    continue
                if err and status != 429:
                    continue

                # Enhanced status code handling
                if status == 200:
                    status_str = f"[bold green]{status} ✅ OK[/bold green]"
                    hits += 1
                elif status in [401, 403]:
                    status_str = f"[bold orange1]{status} 🔒 Forbidden/Unauthorized[/bold orange1]"
                    hits += 1
                elif status in [301, 302, 307, 308]:
                    status_str = f"[bold cyan]{status} → Redirect[/bold cyan]"
                    hits += 1
                elif status == 405:
                    status_str = f"[bold magenta]{status} 🚦 Method Not Allowed (Possible valid endpoint)[/bold magenta]"
                    hits += 1
                elif status == 400:
                    status_str = f"[bold yellow]{status} ⚠️ Bad Request[/bold yellow]"
                elif status == 500:
                    status_str = f"[bold red]{status} 💥 Server Error[/bold red]"
                elif status == 429:
                    status_str = f"[bold yellow]{status} ⏳ Rate Limited[/bold yellow]"
                elif status == 401:
                    status_str = f"[bold orange1]{status} 🔒 Unauthorized[/bold orange1]"
                elif status == 403:
                    status_str = f"[bold orange1]{status} 🔒 Forbidden[/bold orange1]"
                elif status == 503:
                    status_str = f"[bold red]{status} 🚧 Service Unavailable[/bold red]"
                elif status == 202:
                    status_str = f"[bold green]{status} 🕒 Accepted[/bold green]"
                elif status == 201:
                    status_str = f"[bold green]{status} 🆕 Created[/bold green]"
                elif status == 204:
                    status_str = f"[bold green]{status} 🚫 No Content[/bold green]"
                else:
                    status_str = f"[bold white]{status}[/bold white]"

                if status != 429:
                    print(f"[cyan]{url}[/cyan] {status_str}" + (f" → [yellow]{location}[/yellow]" if location else ""))

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        console.print(Panel.fit(
            f"[bold green]🎉 Scan finished![/bold green]\n\n"
            f"[bold]Hits found:[/bold] [yellow]{hits}[/yellow]\n"
            f"[bold]Duration:[/bold] [yellow]{duration:.2f}s[/yellow]",
            title="[bold green]Result[/bold green]", border_style="green"
        ))

async def fetch(session, word, baseUrl, proxy, headers=None):
    if headers is None:
        headers = {"User-Agent": USER_AGENT}
    url = f"{baseUrl}/{word}"
    location = None

    try:
        async with session.get(url, headers=headers, ssl=ssl_context, allow_redirects=False, proxy=proxy) as resp:
            if resp.status == 429:
                return url, 429, None, None
            
            if resp.status in [301, 302, 308]:
                location = resp.headers.get("Location")
            return url, resp.status, location, None
    except Exception as e:
        return url, 0, None, e


async def ping(session, url, timeout, proxy):
    url = url.strip().rstrip("/")
    urls = [url] if url.startswith(("http://", "https://")) else [f"https://{url}", f"http://{url}"]

    for u in urls:
        try:
            ssl_param = False if u.startswith("http://") else ssl_context
            async with session.get(u, headers={"User-Agent": USER_AGENT}, ssl=ssl_param, timeout=timeout, proxy=proxy) as resp:
                return True, u
        except:
            continue
    return False, None