import os
import shutil

from colorama import init, Fore, Style
init()

from configobj import ConfigObj

import fabric_colors


def quickstart():
    """
    Run `fabc-quickstart` in your console to get started with fabric-colors!
    """
    venv = os.path.basename(os.getenv('VIRTUAL_ENV'))
    if venv:
        print "Begin configuring " + Fore.GREEN + "{0}.".format(venv) + Style.RESET_ALL
    else:
        exit()
    a = "y"
    a = raw_input("Ready to go? [y/n]: ")
    while (a == "y"):
        print "Getting started..."

        # Set project_name
        project_home = os.getenv('PROJECT_HOME')
        project_name = raw_input("Your project name is [" + Fore.GREEN + "{0}".format(venv) \
                + Style.RESET_ALL + "]: ")
        if not project_name:
            project_name = venv

        # Set project_root
        print "fabsettings.ini will be created in your project root"
        project_root = os.path.join(project_home, project_name)
        project_root = raw_input("Your project root is [" + Fore.GREEN + "{0}".format(project_root) \
                + Style.RESET_ALL + "]: ")
        if not project_root:
            project_root = os.path.join(project_home, project_name)

        # Ask user to specify nodes
        print "Specify the nodes you will use in your project"
        nodes = {}
        prod, nodes = specify_nodes("prod", nodes)
        dev, nodes = specify_nodes("dev", nodes)
        more_nodes = raw_input("Specify more nodes? [y/n]: ")
        if more_nodes == "y":
            i = 2
        while (more_nodes == "y"):
            current_node = "node_" + str(i)
            node, nodes = specify_nodes(current_node)
            more_nodes = raw_input("Specify more nodes? [y/n]: ")
            i += 1

        # Generate fabsettings.ini based on specified nodes
        config = ConfigObj()
        config.filename = 'fabsettings.ini'
        config.encoding = 'utf8'
        config.indent_type = '    '

        # project section
        config['project'] = {}
        config['project']['name'] = project_name

        # nodes section
        config['nodes'] = {}
        for k, v in nodes.items():
            config['nodes'][k] = {}   # new node section
            config['nodes'][k]['name'] = v['node_name']
            config['nodes'][k]['ip'] = v['node_ip']

        config.write()
        print "Created fabsettings.ini with the following nodes."
        print nodes

        a = None

    # Create fabfile.py
    create_fabfile(project_root)


def create_fabfile(project_root):
    """
    Creates a fabfile.py in the given project_root if it does not exist.
    """
    #project_root = raw_input("Your project root is [" + Fore.GREEN + "{0}".format(project_root) \
            #+ Style.RESET_ALL + "]: ")
    src = os.path.join(fabric_colors.__path__[0], 'fabfile.py.sample')
    dest = os.path.join(project_root, 'fabfile.py')
    if not dest:
        print "You are not in a virtualenv. So please specify the destination \
                directory for your fabfile.py"
        dest = os.path.join(os.getcwd(), 'fabfile.py')
        dest = raw_input("Destination [e.g. " + Fore.GREEN + "%s" + \
                Style.RESET_ALL + "]: " % dest)

    print "Copying the sample fabfile.py.sample from " + Fore.GREEN + src + Style.RESET_ALL
    print "To " + Fore.GREEN + dest + Style.RESET_ALL

    shutil.copyfile(src, dest)
    shutil.copystat(src, dest)


def specify_nodes(name, nodes):
    """
    Accepts the name of a new node and a dictionary of existing nodes.
    Returns the new node with user-provided domain name and ip address and
    a dictionary of all nodes.
    """
    node = raw_input("Specify short name of node [%s] or 'n' for none: " % name)
    if not node or node != "n":
        node = name
        a = 1
    while (a == 1):
        node_name = raw_input("Domain name of %s node [yourdomain.com]: " % name)
        node_ip = raw_input("IP address of %s node [ip.add.re.ss]: " % name)
        if node_name and node_ip:
            a = 0
        else:
            print "Please provide an appropriate domain name and ip address"

    new_node = {node: {'node_name': node_name, 'node_ip': node_ip}}
    nodes[node] = {'node_name': node_name, 'node_ip': node_ip}

    return new_node, nodes
