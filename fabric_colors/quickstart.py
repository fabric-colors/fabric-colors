import os

from colorama import init, Fore, Style
init()


def quickstart():
    """
    Run `fabc-quickstart` in your console to get started with fabric-colors!
    """
    environ = os.path.basename(os.getenv('VIRTUAL_ENV'))
    if environ:
        print "Begin configuring " + Fore.GREEN + "{0}.".format(environ) + Style.RESET_ALL
    else:
        exit()
    a = "y"
    a = raw_input("Ready to go? [y/n]: ")
    if a == "y":
        print "Getting started..."
    else:
        print("Terminating...")
