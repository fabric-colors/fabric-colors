from fabric.api import sudo, run
from fabric_colors.deployment import _env_get


def _server_check_python_symlink():
    """
    Check if python2 symlink to /usr/local/bin/python already exists.
    """
    result = sudo('python_symlink=/usr/local/bin/python; if [ -L $python_symlink ]; then echo 1; else echo ""; fi')
    return result.stdout


def _server_check_virtualenvwrapper(path_bp):
    result = sudo(';if grep -rn "export WORKON_HOME" {0}/.bash_profile > /dev/null 2>&1; then echo 1; else echo ""; fi'.format(path_bp))
    return result.stdout


def _server_python_arch():
    """
    Base python2 install on arch linux.
    """
    sudo('pacman -S python2 --noconfirm')
    if not _server_check_python_symlink():
        sudo('ln -s /usr/bin/python2 /usr/local/bin/python')
    sudo('pacman -S python2-distribute --noconfirm')
    sudo('pacman -S python2-pip --noconfirm')


def _server_virtualenvwrapper_arch(username, systemwide=False):
    """
    Installs virtualenvwrapper and modifes the linux user's bash profile so virtualenvwrapper commands are available. Also updates /etc/skel/.bash_profile so that new users thus created will inherit the same .bash_profile. `_server_virtualenvwrapper_arch(username, systemwide=True)`
    """
    path_bp = '/home/{0}'.format(username)
    if systemwide == True:
        path_bp = '/etc/skel'

    run('pip2 install virtualenvwrapper')

    if not _server_check_virtualenvwrapper(path_bp):
        print("virtualenvwrapper hasn't been installed in {0}/.bash_profile yet. Installing...".format(path_bp))
        run('echo \'export WORKON_HOME=$HOME/.virtualenvs\' >> {0}/.bash_profile'.format(path_bp))
        run('echo \'export PROJECT_HOME=$HOME/work\' >> {0}/.bash_profile'.format(path_bp))
        run('echo \'source `which virtualenvwrapper.sh`\' >> {0}/.bash_profile'.format(path_bp))
    else:
        print("virtualenvwrapper has been installed in {0}/.bash_profile already.".format(path_bp))


def server_postgresql_install(username, target):
    _env_get(target)
    sudo('pacman -S postgresql --noconfirm')


def server_postgresql_start(username, target):
    _env_get(target)
    if not server_postgresql_status(username, target):
        sudo('rc.d start postgresql')


def server_postgresql_stop(username, target):
    _env_get(target)
    if server_postgresql_status(username, target):
        sudo('rc.d stop postgresql')


def server_postgresql_status(username, target):
    _env_get(target)
    print("Checking the status of our postgresql database")
    result = run(';if ps aux | grep -v grep | grep -i "postgres"; \
            then echo 1; else echo ""; fi')
    print result.stdout
