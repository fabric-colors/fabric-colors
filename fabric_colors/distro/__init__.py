from fabric.api import env, run
from fabric_colors.deployment import _env_get
from fabsettings import PROJECT_SITES


def server_adduser(username, target):
    """
    Create user given the user name & target machine. e.g. `fab server_adduser:web,dev`
    """
    print("This command can only be executed by the root user")
    _env_get(target)
    env.user = 'root'
    if not server_chkuser(username, target):
        run('useradd -m {0}'.format(username))
        run('passwd {0}'.format(username))
        run('gpasswd -a {0} wheel'.format(username))
        print("We can now execute commands as this user on your target machine.")
        print("To avoid having to key in this user's password everytime we access the target machine, do:")
        print("ssh-copy-id -i ~/.ssh/id_rsa.pub {0}@{1}".format(username, PROJECT_SITES[target]['NAME']))
    print("user {0} already exists on {1}. Not adding.".format(username, target))


def server_deluser(username, target):
    """
    Delete user & its home directory given the user name & target machine. e.g. `fab server_deluser:web,dev`
    """
    print("This command can only be executed by the root user")
    _env_get(target)
    env.user = 'root'
    run('userdel -r {0}'.format(username))


def server_chkuser(username, target):
    """
    Check if the given user name is available on the given target machine e.g. `fab server_chkuser:web,dev` and returns 1 (True) or Nothing (False)
    """
    _env_get(target)
    env.user = 'root'
    result = run(';if id -u "{0}" > /dev/null 2>&1; then \
                        echo 1; \
                    else \
                        echo ""; \
                    fi'.format(username))
    return result.stdout


def server_distro(username, target):
    _env_get(target)
    env.user = username
    result = run('cat /etc/*-release')
    import re
    result_list = re.findall(r'([^=\s,]+)=([^=\s,]+)', result)
    for item in result_list:
        if item[0] == 'ID':
            return item[1]
    return None


def server_visudo(target):
    """
    Assign sudo rights to all users in the wheel group on arch linux. e.g. ` fab server_visudo:dev`
    """
    _env_get(target)
    env.user = 'root'
    run("""
            if [ -e /etc/sudoers.tmp -o "$(pidof visudo)" ]; then
                echo $(pidof visudo)
                echo "/etc/sudoers busy, try again later"
                exit 1
            fi

            cp -p /etc/sudoers /etc/sudoers.bak
            cp -p /etc/sudoers /etc/sudoers.tmp

            line="%wheel ALL=(ALL) ALL"

            sed -i "/${line}/ s/# *//" /etc/sudoers.tmp

            mv /etc/sudoers.tmp /etc/sudoers

            exit 0
        """)


def server_python(username, target, distro="arch"):
    """
    Sets up the python environment, given the username, target and distro (defaults to arch). e.g. `fab server_python:web,dev`
    """
    _env_get(target)
    if distro == "arch":
        from fabric_colors.distro.arch import _server_python_arch, \
                _server_virtualenvwrapper_arch
        _server_python_arch()
        _server_virtualenvwrapper_arch(username, systemwide=True)
        _server_virtualenvwrapper_arch(username)


def server_postgresql(username, target, distro):
    if distro == "arch":
        from fabric_colors.distro.arch import _server_postgresql
        _server_postgresql(username, target)


def server_setup(username, target):
    """
    Runs all scripts as given username, in sudo mode, on the target server. e.g. `fab server_setup:web,dev`
    """
    _env_get(target)
    env.user = username
    distro = server_distro(username, target)
    if distro:
        print("Setting up {0}, running on {1}, with {2}".format(target, distro, username))
        server_python(username, target, distro)
        from fabric_colors.distro.arch import server_postgresql_status
        server_postgresql_status(username, target)
        #server_postgresql(username, target, distro)
