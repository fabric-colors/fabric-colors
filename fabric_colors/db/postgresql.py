from fabric.api import task, sudo, run

from fabric_colors.environment import set_target_env


@task
@set_target_env
def install():
    sudo('pacman -S postgresql --noconfirm')
    if status():
        print('Postgresql is already running.')
    else:
        print('Postgresql is not running.')
        if not chk_data_dir():
            print("Set up postgresql for the first time on this host")
            setup_data_dir()
            initializer()

        print("Postgresql's data directory is ready. So start the server.")
        start()


@task
@set_target_env
def chk_data_dir():
    path = "/var/lib/postgres/data"
    cmd = """if [ -e "{0}" ]; then echo 1; else echo ""; fi""".format(path)
    return run(cmd)


@task
@set_target_env
def initializer():
    print("Set-up initialization script for postgresql")
    sudo("systemctl enable postgresql")


@task
@set_target_env
def setup_data_dir():
    path_postgres = "/var/lib/postgres"
    path_data = "/var/lib/postgres/data"
    cmd1 = "mkdir -p {0}".format(path_data)
    cmd2 = "chown -R postgres:postgres {0}".format(path_postgres)
    cmd3 = """su - postgres -c 'initdb --locale en_US.UTF-8 -D "{0}"'""".format(path_data)
    sudo(cmd1)
    sudo(cmd2)
    sudo(cmd3)


@task
@set_target_env
def start():
    print("Starting postgresql")
    if not status():
        sudo('systemctl start postgresql')


@task
@set_target_env
def stop():
    print("Stopping postgresql")
    if status():
        sudo('systemctl stop postgresql')


@task
@set_target_env
def restart():
    print("Restarting postgresql")
    sudo('systemctl restart postgresql')


@task
@set_target_env
def status():
    print("Checking the status of our postgresql database")
    result = sudo('if ps aux | grep -v grep | grep -i "postgres"; then echo 1; else echo ""; fi')
    return result
