from fabric.api import task, sudo, run

from fabric_colors.environment import set_target_env


@task
@set_target_env
def installed():
    """
    Check if mongodb is installed.
    """
    pkg = "pacman -Qs mongodb"
    cmd = """
        pkg=`{0}`
        if [ -n "$pkg" ]; then echo 1; else echo ""; fi""".format(pkg)
    return run(cmd)


@task
@set_target_env
def install():
    """
    Install mongodb and start it if it isn't running.
    """
    if not installed():
        sudo('pacman -S mongodb --noconfirm')

    if status():
        print('Mongodb is already running.')
    else:
        print('Mongodb is not running.')
        initializer()
        start()


@task
@set_target_env
def status():
    """
    Is mongodb already running?
    """
    print("Checking the status of mongodb")
    result = sudo('if ps aux | grep -v grep | grep -i "mongodb"; then echo 1; else echo ""; fi')
    return result


@task
@set_target_env
def start():
    """
    Start mongodb
    """
    print("Starting mongodb")
    if not status():
        sudo('systemctl start mongodb')


@task
@set_target_env
def stop():
    """
    Stop mongodb
    """
    print("Stopping mongodb")
    sudo('systemctl stop mongodb')


@task
@set_target_env
def restart():
    """
    Restart mongodb
    """
    print("Restarting mongodb")
    sudo('systemctl restart mongodb')


@task
@set_target_env
def initializer():
    """
    Enable initializer for mongodb
    """
    print("Set-up initialization script for mongodb")
    sudo("systemctl enable mongodb")
