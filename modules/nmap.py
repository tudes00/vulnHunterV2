import subprocess
import questionary
import os
import sys
from rich import print

# TODO:
# rajouter different format output xml tout ça

from rich.traceback import install
install(show_locals=True)

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

def nmap():
    from main import display_tools
    
    try:
        use_template = questionary.confirm("Do you want to use a scan template?").ask()
        template_params = None
        if use_template:
            templates = {
                "Quick Scan": {
                    "params": "-T4 -F",
                    "desc": "Fast scan of common ports."
                },
                "Regular Scan": {
                    "params": "",
                    "desc": "Default Nmap scan."
                },
                "Ping Scan": {
                    "params": "-sn",
                    "desc": "Host discovery only (no port scan)."
                },
                "Slow Comprehensive Scan": {
                    "params": "-sS -sU -T4 -A -v -PE -PP -PS80,443 -PA3389 -PU40125 -PY -g 53 --script \"default or (discovery and safe)\"",
                    "desc": "Thorough scan with many checks (slow)."
                },
                "Intense Scan": {
                    "params": "-T4 -A -v",
                    "desc": "Aggressive scan with OS/service detection."
                },
                "Service Version Detection": {
                    "params": "-sV",
                    "desc": "Detect service versions on open ports."
                },
                "OS Detection": {
                    "params": "-O",
                    "desc": "Detect operating system."
                },
                "TCP SYN Stealth Scan": {
                    "params": "-sS",
                    "desc": "Stealthy TCP SYN scan."
                },
                "HTTP Enumeration": {
                    "params": "-p 80,443 --script=http-title,http-methods,http-backup-finder",
                    "desc": "Enumerate HTTP services."
                },
                "Vuln Scan": {
                    "params": "--script=vuln",
                    "desc": "Run vulnerability scripts."
                },
                "SSL Scan": {
                    "params": "-p 443 --script=ssl-cert,ssl-enum-ciphers",
                    "desc": "Check SSL certificate and ciphers."
                },
                "FTP Scan": {
                    "params": "-p 21 --script=ftp-anon,ftp-bounce",
                    "desc": "Check FTP for anonymous login and bounce."
                },
                "SSH Scan": {
                    "params": "-p 22 --script=ssh-hostkey",
                    "desc": "Get SSH host keys."
                },
                "Discovery Scripts": {
                    "params": "--script=discovery",
                    "desc": "Run discovery scripts."
                },
                "ARP Scan": {
                    "params": "-PR",
                    "desc": "ARP scan for local network hosts."
                },
                "Traceroute": {
                    "params": "--traceroute",
                    "desc": "Perform traceroute to target."
                },
            }

            template_choices = [
                questionary.Choice(
                    title=f"{name.upper()} - {tpl['desc'].capitalize()}",
                    value=name
                )
                for name, tpl in templates.items()
            ]
            template_choice = questionary.select(
                "Choose a scan template:",
                choices=template_choices
            ).ask()
            if template_choice is None:
                display_tools()
                return
            template_params = templates[template_choice]["params"]

        while True:
            target = questionary.text("Enter the target to scan (IP or domain):").ask()
            if target:
                break
            if target is None:
                display_tools()
                return
            print("[bold red]No target provided. Please enter a target.[/bold red]")

        if use_template:
            params = template_params
        else:
            params = questionary.text("Additional Nmap parameters (e.g., -sV -p 80,443) [leave empty for default]:").ask()
            if not params:
                params = "-sV"

        save_output = questionary.confirm("Do you want to save the output to a text file?").ask()

        output_file = None
        if save_output:
            import re
            def sanitize_filename(name):
                name = re.sub(r'^https?://', '', name)
                name = re.sub(r'[\\/*?:"<>|]', '_', name)
                return name

            while True:
                user_input = questionary.text("Output file name (e.g., result.txt) [leave empty for default]:").ask()
                if user_input is None: 
                    display_tools()
                    return

                safe_target = sanitize_filename(target)
                safe_user_input = sanitize_filename(user_input) if user_input else None
                output_file = "output/nmap/" + (safe_user_input if safe_user_input else safe_target + ".txt")
                
                if os.path.isfile(output_file):
                    overwrite = questionary.confirm(f"The file '{output_file}' already exists. Overwrite?").ask()
                    if not overwrite:
                        print("[bold yellow]Operation cancelled. Choose another file name.[/bold yellow]")
                        continue
                break

        cmd = ["nmap"] + (params.split() if params else []) + [target]
        if save_output and output_file:
            cmd += ["-oN", output_file]

        print(f"\n[bold red]Executing command: {' '.join(cmd)}[/bold red]\n")

        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            check=True
        )
        print(result.stdout)

    except KeyboardInterrupt:
        display_tools()
    except subprocess.CalledProcessError as e:
        print(f"[bold red]Error during scan: {e.stderr}[/bold red]")
    except FileNotFoundError:
        print("[bold red]Nmap is not installed or not found in PATH.[/bold red]")