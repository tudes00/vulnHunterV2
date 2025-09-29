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
from utils.utils import defaultWordlistDirFinder, USER_AGENTS, defaultWordlistDirFinderRecursive

console = Console()


def backup():
  from main import display_tools

  try:
    console.print(
        Panel.fit("[bold red]Welcome to DirFinder![/bold red]\n",
                  title="DirFinder",
                  subtitle="Directory Scanner"))

    while True:
      target = questionary.text("Enter the target to scan:").ask()
      if target: break
      if target is None:
        display_tools()
        return
      print("[bold red]No target provided. Please enter a target.[/bold red]")

    while True:
      user_input = questionary.text(
          "Wordlist path [leave empty for default]:").ask()
      if user_input is None:
        display_tools()
        return
  except KeyboardInterrupt:
    display_tools()
