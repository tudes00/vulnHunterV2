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

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))
from utils.utils import defaultWordlistDirFinder, USER_AGENTS, defaultWordlistDirFinderRecursive

console = Console()

#TODO improve ssl handling
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

#TODO rajouter pour les 429 tout ça le proxy rotation

PROXY = ["testt zebii la mouche"]


def dirFinder():
    from main import display_tools
    building = True

    try:
        console.print(
            Panel.fit("[bold red]Welcome to DirFinder![/bold red]\n",
                      title="DirFinder",
                      subtitle="Directory Scanner"))

        while True:
            target = questionary.text("Enter the target to scan:").ask()
            if target:
                break
            if target is None:
                display_tools()
                return
            print(
                "[bold red]No target provided. Please enter a target.[/bold red]"
            )

        while True:
            user_input = questionary.text(
                "Wordlist path [leave empty for default]:").ask()
            if user_input is None:
                display_tools()
                return

            base_dir = os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "../"))
            if user_input:
                wordlist = os.path.abspath(
                    os.path.expanduser(user_input)) if os.path.isabs(
                        user_input) else os.path.join(base_dir, user_input)
            else:
                wordlist = os.path.join(base_dir, defaultWordlistDirFinder)

            if os.path.isfile(wordlist):
                print(f"[bold green]Using wordlist:[/bold green] {wordlist}")
                break
            else:
                print(
                    f"[bold red]The file {wordlist} does not exist![/bold red]"
                )

        max_threads = questionary.text(
            "Enter max concurrent requests [default 500]:").ask()
        try:
            max_threads = int(max_threads) if max_threads else 500
        except ValueError:
            max_threads = 500

        timeout = questionary.text(
            "Enter max timeout for requests [default 2]:").ask()
        try:
            timeout = int(timeout) if timeout else 2
        except ValueError:
            timeout = 2

        proxy_input = questionary.text(
            "Proxy (format http://127.0.0.1:8080) [leave empty for none]:"
        ).ask()
        proxy = proxy_input.strip() if proxy_input else None

        recursiveExploration = questionary.confirm(
            "Want to use recursive exploration(This may take a while)?",
            default=
            True  #add in settings the option to set it to true by default, change wordlist used by this, maxdepth; ...
        ).ask()

        save_output = questionary.confirm(
            "Do you want to save the output to a text file?").ask()

        output_file = None
        if save_output:
            import re

            def sanitize_filename(name):
                name = re.sub(r'^https?://', '', name)
                name = re.sub(r'[\\/*?:"<>|]', '_', name)
                return name

            while True:
                user_input = questionary.text(
                    "Output file name (e.g., result.txt) [leave empty for default]:"
                ).ask()
                if user_input is None:
                    display_tools()
                    return

                safe_target = sanitize_filename(target)
                safe_user_input = sanitize_filename(
                    user_input) if user_input else None
                output_file = "output/dirFinder/" + (
                    safe_user_input if safe_user_input else safe_target +
                    ".txt")

                if os.path.isfile(output_file):
                    overwrite = questionary.confirm(
                        f"The file '{output_file}' already exists. Overwrite?"
                    ).ask()
                    if not overwrite:
                        print(
                            "[bold yellow]Operation cancelled. Choose another file name.[/bold yellow]"
                        )
                        continue
                break

        console.print(
            Panel.fit(
                f"Target: [bold yellow]{target}[/bold yellow]\nWordlist: [bold yellow]{wordlist}[/bold yellow]\nMax concurrent requests: [bold yellow]{max_threads}[/bold yellow]\nMax timeout: [bold yellow]{timeout}[/bold yellow]\nUse recursive exploration: [bold yellow]{recursiveExploration}[/bold yellow]\nProxy: [bold yellow]{proxy}[/bold yellow]\nOutput: [bold yellow]{output_file}[/bold yellow]",
                title="Scan Summary",
                border_style="bold red"))

        confirm = questionary.confirm(
            "Start scan with the above settings?").ask()
        if not confirm:
            print("[bold red]Scan cancelled.[/bold red]")
            display_tools()
            return

        building = False
        asyncio.run(
            start(target, wordlist, max_threads,
                  aiohttp.ClientTimeout(total=timeout), proxy,
                  recursiveExploration, output_file))

    except KeyboardInterrupt:
        if building:
            print("\n[bold red]Interrupted by user.[/bold red]")
            display_tools()


async def start(target, wordlistPath, max_threads, timeout, proxy,
                recursiveExploration, output_file):

    #target="localhost:8000"

    now = datetime.datetime.now()
    console.print(
        Panel.fit(
            f"[bold cyan] Starting DirFinder scan[/bold cyan]\n\n"
            f"[bold]Date:[/bold] [yellow]{now.strftime('%d/%m/%Y %H:%M:%S')}[/yellow]\n"
            f"[bold]Target:[/bold] [magenta]{target}[/magenta]\n"
            f"[bold]Wordlist:[/bold] [green]{wordlistPath}[/green]",
            title="[bold red]Scan in progress[/bold red]",
            border_style="bold red"))

    start_time = datetime.datetime.now()
    conn = aiohttp.TCPConnector(limit=max_threads * 2, family=0, ssl=False)

    async with aiohttp.ClientSession(connector=conn,
                                     timeout=timeout) as session:
        alive, validUrl = await ping(session, target, timeout, proxy)
        if not alive:
            console.print(
                Panel.fit("[bold red]❌ Host seems down[/bold red]",
                          title="[bold red]Result[/bold red]"))
            return

        console.print(
            f"[bold green]✅ Host is up![/bold green] URL used: [cyan]{validUrl}[/cyan]"
        )

        with open(wordlistPath, "r", encoding="utf-8") as f:
            words = [w.strip().lstrip("/") for w in f if w.strip()]
        random.shuffle(words)

        hits = 0
        hitsText = []
        semaphore = asyncio.Semaphore(max_threads)

        async def fetch_with_retries(word, session, validUrl, proxy,
                                     semaphore):
            url = f"{validUrl}/{word}"
            max_attempts = 10
            for attempt in range(max_attempts):
                async with semaphore:
                    await asyncio.sleep(random.uniform(0.05, 0.25))
                    headers = {"User-Agent": random.choice(USER_AGENTS)}
                    try:
                        url, status, location, err = await fetch(
                            session, word, validUrl, proxy, headers)
                    except Exception as e:
                        status, location, err = 0, None, e
                if status == 429 or isinstance(
                        err, (ClientConnectorError, ClientOSError,
                              ServerDisconnectedError, ClientResponseError)):
                    wait_time = (5**attempt) + random.uniform(0, 2)
                    if attempt == max_attempts - 1:
                        print(
                            f"[bold red]🚨 Error for url {url} after {max_attempts} attempts: {err}[/bold red]"
                        )
                    await asyncio.sleep(wait_time)
                else:
                    return url, status, location, err, word
            return url, status, location, err, word

        progress = Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(), TaskProgressColumn(), TimeElapsedColumn(),
            TextColumn(
                "[bold blue]{task.completed}[/bold blue]/[bold yellow]{task.total}[/bold yellow] words"
            ))

        with progress:
            task1 = progress.add_task("Scanning...", total=len(words))
            recursive_tasks = []

            coros = [
                fetch_with_retries(w, session, validUrl, proxy, semaphore)
                for w in words
            ]
            for fut in asyncio.as_completed(coros):
                url, status, location, err, word = await fut
                progress.update(task1, advance=1)

                if isinstance(status, Exception) or status == 404:
                    continue
                if err and status != 429:
                    continue

                hit, status_str = getEnhancedStatus(status)
                hits += hit
                hitsText.append(url)

                if status != 429:
                    print(f"[cyan]{url}[/cyan] {status_str}" + (
                        f" → [yellow]{location}[/yellow]" if location else ""))
                    if recursiveExploration:
                        recursive_tasks.append(word)

            MAX_DEPTH = 5
            current_depth = 1

            recursive_tasks = [[word] for word in recursive_tasks]

            while recursiveExploration and current_depth <= MAX_DEPTH and recursive_tasks:
                new_wordlist = defaultWordlistDirFinderRecursive if os.path.isfile(
                    os.path.join(
                        os.path.dirname(os.path.abspath(__file__)), "../",
                        defaultWordlistDirFinderRecursive)) else wordlistPath
                with open(new_wordlist, "r", encoding="utf-8") as f:
                    newWords = [w.strip().lstrip("/") for w in f if w.strip()]
                random.shuffle(newWords)

                print(
                    f"[bold blue]🔍 Starting recursive scan with depth {current_depth}...[/bold blue]"
                )
                next_recursive_tasks = []
                for path_parts in recursive_tasks:
                    base_path = "/".join(path_parts)
                    url = f"{validUrl}/{base_path}"

                    progress.update(
                        task1,
                        description=f"Recursive scanning /{base_path}...")
                    progress.update(task1, total=len(newWords), completed=0)
                    coros = [
                        fetch_with_retries(f"{base_path}/{newWord}", session,
                                           validUrl, proxy, semaphore)
                        for newWord in newWords
                    ]
                    for fut in asyncio.as_completed(coros):
                        url, status, location, err, word = await fut
                        progress.update(task1, advance=1)

                        if isinstance(status, Exception) or status == 404:
                            continue
                        if err and status != 429:
                            continue

                        hit, status_str = getEnhancedStatus(status)

                        hits += hit
                        hitsText.append(url)

                        if status != 429:
                            print(f"[cyan]{url}[/cyan] {status_str}" +
                                  (f" → [yellow]{location}[/yellow]"
                                   if location else ""))
                            if recursiveExploration:
                                next_recursive_tasks.append(
                                    path_parts + [word.split('/')[-1]])
                recursive_tasks = next_recursive_tasks
                current_depth += 1
            progress.update(task1, description="Scan complete.")

        end_time = datetime.datetime.now()
        duration = (end_time - start_time).total_seconds()
        console.print(
            Panel.fit(
                f"[bold green]🎉 Scan finished![/bold green]\n\n"
                f"[bold]Hits found:[/bold] [yellow]{hits}[/yellow]\n"
                f"[bold]Duration:[/bold] [yellow]{duration:.2f}s[/yellow]",
                title="[bold green]Result[/bold green]",
                border_style="green"))
        if output_file:
            with open(output_file, 'w') as output:
                output.write("\n".join(hitsText) + "\n")
            console.print(
                f"[bold green]✅ Output saved to {output_file}[/bold green]")


def getEnhancedStatus(status):
    hit = 0
    if status == 200:
        status_str = f"[bold green]{status} ✅ OK[/bold green]"
        hit += 1
    elif status in [401, 403]:
        status_str = f"[bold orange1]{status} 🔒 Forbidden/Unauthorized[/bold orange1]"
        hit += 1
    elif status in [301, 302, 307, 308]:
        status_str = f"[bold cyan]{status} → Redirect[/bold cyan]"
        hit += 1
    elif status == 405:
        status_str = f"[bold magenta]{status} 🚦 Method Not Allowed (Possible valid endpoint)[/bold magenta]"
        hit += 1
    elif status == 400:
        status_str = f"[bold yellow]{status} ⚠️ Bad Request[/bold yellow]"
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
    return hit, status_str


async def fetch(session, word, baseUrl, proxy, headers=None):
    url = f"{baseUrl}/{word}"
    location = None

    try:
        async with session.get(url,
                               headers=headers,
                               ssl=ssl_context,
                               allow_redirects=False,
                               proxy=proxy) as resp:
            if resp.status == 429:
                return url, 429, None, None

            if resp.status in [301, 302, 308]:
                location = resp.headers.get("Location")
            return url, resp.status, location, None
    except Exception as e:
        return url, 0, None, e


async def ping(session, url, timeout, proxy):
    url = url.strip().rstrip("/")
    urls = [url] if url.startswith(
        ("http://", "https://")) else [f"https://{url}", f"http://{url}"]

    for u in urls:
        try:
            ssl_param = False if u.startswith("http://") else ssl_context
            async with session.get(
                    u,
                    headers={"User-Agent": random.choice(USER_AGENTS)},
                    ssl=ssl_param,
                    timeout=timeout,
                    proxy=proxy) as resp:
                return True, u
        except:
            continue
    return False, None
