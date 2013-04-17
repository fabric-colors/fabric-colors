from fabric.api import task, sudo, run, env

from fabric_colors.environment import set_target_env


@task
@set_target_env
def install(username):
    sudo('pacman -S postgresql --noconfirm')


@task
@set_target_env
def start(username):
    if not status(username):
        sudo('systemctl start postgresql')


@task
@set_target_env
def stop(username):
    if status(username):
        sudo('systemctl stop postgresql')


@task
@set_target_env
def status(username):
    print("Checking the status of our postgresql database")
    result = run('if ps aux | grep -v grep | grep -i "postgres"; then echo 1; else echo ""; fi')
    print result.stdout


@task
@set_target_env
def postgresql(username, distro):
    if distro == "arch":
        from fabric_colors.distro.arch import _server_postgresql
        _server_postgresql(username, env.host)
