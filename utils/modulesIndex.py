import sys
import os

sys.path.append(
    os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

from modules.nmap import nmap as nmapModule
from modules.dirFinder import dirFinder as dirFinderModule
from modules.full import full as fullModule
from modules.vuln import vuln as vulnMobule
from modules.settings import settings as settingsModule


def nmap():
    nmapModule()


def dirFinder():
    dirFinderModule()


def full():
    fullModule()


def vuln():
    vulnMobule()


def settings():
    settingsModule()
