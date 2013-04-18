from fabric.api import task, sudo, run

from fabric_colors.environment import set_target_env


@task
@set_target_env
def installed():
    """
    Check if nginx is installed.
    """
    pkg = "pacman -Qs nginx"
    cmd = """
        pkg=`{0}`
        if [ -n "$pkg" ]; then echo 1; else echo ""; fi""".format(pkg)
    return run(cmd)


@task
@set_target_env
def install():
    """
    Install nginx and start it if it isn't running.
    """
    if not installed():
        sudo('pacman -S nginx --noconfirm')

    if status():
        print('nginx is already running.')
    else:
        print('nginx is not running.')
        initializer()
        start()


@task
@set_target_env
def status():
    """
    Is nginx already running?
    """
    print("Checking the status of nginx")
    result = sudo('if ps aux | grep -v grep | grep -i "nginx"; then echo 1; else echo ""; fi')
    return result


@task
@set_target_env
def start():
    """
    Start nginx
    """
    print("Starting nginx")
    if not status():
        sudo('systemctl start nginx')


@task
@set_target_env
def stop():
    """
    Stop nginx
    """
    print("Stopping nginx")
    sudo('systemctl stop nginx')


@task
@set_target_env
def restart():
    """
    Restart nginx
    """
    print("Restarting nginx")
    sudo('systemctl restart nginx')


@task
@set_target_env
def initializer():
    """
    Enable initializer for nginx
    """
    print("Set-up initialization script for nginx")
    sudo("systemctl enable nginx")
