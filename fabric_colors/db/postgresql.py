import os

from fabric.api import task, env
from fabric.operations import local
from fabric.colors import red, green

from fabric_colors.environment import set_target_env


@task
@set_target_env
def install():
    """
    Distro-agnostic way of installing postgresql.
    """
    mod = __import__('fabric_colors.distro.{0}.postgresql'.format(env.distro), fromlist=['{0}.postgresql'.format(env.distro)])
    PKG_INSTALL = getattr(mod, 'PKG_INSTALL')
    PKG_CLIENT_INSTALL = getattr(mod, 'PKG_CLIENT_INSTALL')

    result1, result2 = installed()

    if not result1:
        env.run(PKG_INSTALL)

    if result2 == "No client":
        pass
    elif not result2:
        env.run(PKG_CLIENT_INSTALL)

    if not status():
        if not chk_data_dir():
            print(green("Setting up postgresql for the first time on this host."))
            setup_data_dir()
            initializer()

        start()


@task
@set_target_env
def installed():
    """
    Distro-agnostic way of checking if postgresql is installed.
    """
    mod = __import__('fabric_colors.distro.{0}.postgresql'.format(env.distro), fromlist=['{0}.postgresql'.format(env.distro)])
    cmd1 = getattr(mod, 'PKG_INSTALLED_CMD')
    cmd2 = getattr(mod, 'PKG_CLIENT_INSTALLED_CMD')

    result2 = "No client"
    if env.run == local:
        result1 = local(cmd1, capture=True)
        if cmd2:
            result2 = local(cmd2, capture=True)
    else:
        result1 = env.run(cmd1)
        if cmd2:
            result2 = env.run(cmd2)

    if result1:
        print(green("Server already installed."))
    else:
        print(red("Server not yet installed."))

    if result2 == "No client":
        print(green("This distro does not need a client package for postgresql"))
    elif int(result2) == 1:
        print(green("Client already installed."))
    else:
        print(red("Client not yet installed."))

    return result1, result2


@task
@set_target_env
def status():
    """
    Distro-agnostic checking postgresql status
    """
    cmd = 'if ps aux | grep -v grep | grep -i "postgres"; then echo 1; else echo 0; fi'
    if env.run == local:
        result = local(cmd, capture=True)
    else:
        result = env.run(cmd)

    if result:
        print(green("Postgresql server is running."))
    else:
        print(red("Postgresql server is not running."))

    return result


@task
@set_target_env
def chk_data_dir():
    """
    Distro-agnostic checking postgresql's data directory
    """
    mod = __import__('fabric_colors.distro.{0}.postgresql'.format(env.distro), fromlist=['{0}.postgresql'.format(env.distro)])
    DEFAULT_DATA_DIR = getattr(mod, 'DEFAULT_DATA_DIR')
    cmd = """if [ -e "{0}" ]; then echo 1; else echo ""; fi"""\
            .format(DEFAULT_DATA_DIR)

    if env.run == local:
        result = local(cmd, capture=True)
    else:
        result = env.run(cmd)

    if result:
        print(green("Postgresql server's data directory is present."))
    else:
        print(red("Postgresql server's data directory is not present."))

    return result


@task
@set_target_env
def setup_data_dir():
    """
    Distro-agnostic: set up postgresql data directory
    """
    mod = __import__('fabric_colors.distro.{0}.postgresql'.format(env.distro), fromlist=['{0}.postgresql'.format(env.distro)])
    DEFAULT_DATA_DIR = getattr(mod, 'DEFAULT_DATA_DIR')
    DEFAULT_POSTGRES_DIR = os.path.dirname(DEFAULT_DATA_DIR)
    INITIALIZE_DB = getattr(mod, 'INITIALIZE_DB')
    cmd1 = "sudo mkdir -p {0}".format(DEFAULT_DATA_DIR)
    cmd2 = "sudo chown -R postgres:postgres {0}".format(DEFAULT_POSTGRES_DIR)
    cmd3 = INITIALIZE_DB

    if env.run == local:
        local(cmd1, capture=True)
        local(cmd2, capture=True)
        local(cmd3, capture=True)
    else:
        env.run(cmd1)
        env.run(cmd2)
        env.run(cmd3)


@task
@set_target_env
def initializer():
    """
    Distro-agnostic: set up initializations script for postgresql
    """
    print(green("Set-up initialization script for postgresql"))
    mod = __import__('fabric_colors.distro.{0}.postgresql'.format(env.distro), fromlist=['{0}.postgresql'.format(env.distro)])
    INITIALIZER = getattr(mod, 'INITIALIZER')
    env.run(INITIALIZER)


@task
@set_target_env
def start():
    """
    Distro-agnostic: start postgresql
    """
    print(green("Starting postgresql"))
    mod = __import__('fabric_colors.distro.{0}.postgresql'\
            .format(env.distro), fromlist=['{0}.postgresql'.format(env.distro)])
    START = getattr(mod, 'START')
    if not status():
        env.run(START)


@task
@set_target_env
def stop():
    """
    Distro-agnostic: stop postgresql
    """
    print(green("Stopping postgresql"))
    mod = __import__('fabric_colors.distro.{0}.postgresql'\
            .format(env.distro), fromlist=['{0}.postgresql'.format(env.distro)])
    STOP = getattr(mod, 'STOP')
    if status():
        env.run(STOP)


@task
@set_target_env
def restart():
    """
    Distro-agnostic: restart postgresql
    """
    print(green("Restarting postgresql"))
    mod = __import__('fabric_colors.distro.{0}.postgresql'.format(env.distro), fromlist=['{0}.postgresql'.format(env.distro)])
    RESTART = getattr(mod, 'RESTART')
    env.run(RESTART)
