from fabric.api import env, run, local, task
from fabric.colors import green, red, magenta, cyan

from fabric_colors.environment import set_target_env


@task
@set_target_env
def useradd(username, group="sudo", pubkey=True):
    """
    Usage: `fab -R all server.useradd:web`. Create user given the user name & target machine.
    """
    print("This command can only be executed by the root user")
    env.user = 'root'
    if not userchk(username):
        run('useradd -m {0}'.format(username))
        run('passwd {0}'.format(username))
        run('gpasswd -a {0} {1}'.format(username, group))
        print("We can now execute commands as this user on your target machine.")
        if pubkey:
            print("Add your public key to {0}@{1}".format(username, env.host))
            ssh_copy_id(username)
        else:
            print("Not adding your public key")
            print("To avoid having to key in this user's password everytime we access the target machine, do:")
            print("ssh-copy-id -i ~/.ssh/id_rsa.pub {0}@{1}".format(username, env.host))
    print("user {0} already exists on {1}. Not adding.".format(username, env.host))


@task
@set_target_env
def ssh_copy_id(username=None):
    """
    Usage: `fab -R all server.ssh_copy_id`. Add local machine's public key to target's username
    """
    if not username:
        username = env.user
    user_and_host = "{0}@{1}".format(username, env.host)
    print("Copying your public key to {0}".format(user_and_host))
    local("ssh-copy-id -i ~/.ssh/id_rsa.pub {0}".format(user_and_host))


@task
@set_target_env
def userdel(username):
    """
    Usage: `fab -R all server.userdel:web`. Delete user & its home directory given the user name & target machine.
    """
    print("This command can only be executed by the root user")
    env.user = 'root'
    run('userdel -r {0}'.format(username))


@task
@set_target_env
def userchk(username):
    """
    Usage: `fab -R all server.userchk:web`. Check if the given user name is available on the given target host(s).
    """
    env.user = 'root'
    result = run('if id -u "{0}" > /dev/null 2>&1; then \
                        echo 1; \
                   else \
                        echo ""; \
                   fi'.format(username))
    return result.stdout


@task
@set_target_env
def groups():
    """
    Usage: `fab -R dev server.groups`. Returns available groups.
    """
    available_groups = run('groups').split()
    return available_groups


@task
@set_target_env
def groupadd(group):
    """
    Usage: `fab -R dev server.groupadd:sudo`. Adds the given group.
    """
    env.user = 'root'
    run('groupadd {0}'.format(group))


@task
@set_target_env
def visudo(sudogroup="sudo"):
    """
    Usage: `fab -R all server.visudo:sudogroup`. Enable the given sudo group in /etc/sudoers programmatically.

    This is the same as typing `visudo` and manually commenting out a commented line for the group so it
    has ALL=(ALL) ALL access rights, i.e. sudo rights.
    """
    env.user = 'root'
    if sudogroup not in groups():
        groupadd(sudogroup)

    run("""
            if [ -e /etc/sudoers.tmp -o "$(pidof visudo)" ]; then
                echo $(pidof visudo)
                echo "/etc/sudoers busy, try again later"
                exit 1
            fi

            cp -p /etc/sudoers /etc/sudoers.bak
            cp -p /etc/sudoers /etc/sudoers.tmp

            sed -i "/%{0}\s\+ALL=(ALL) ALL/ s/# *//" /etc/sudoers.tmp

            mv /etc/sudoers.tmp /etc/sudoers

            exit 0
        """.format(sudogroup))


@task
@set_target_env
def setup():
    """
    Usage: `fab -R all server.setup`. Runs all scripts as given username, in sudo mode, on the target server.
    """
    from fabric_colors.distro import distro
    current_distro = distro()
    if current_distro:
        print("Setting up {0}, running on {1}, with {2}".format(env.target, env.distro, env.user))
        setup_base(current_distro)
        setup_python(current_distro)


@task
@set_target_env
def setup_base(distro="arch"):
    """
    Usage: `fab -R dev server.setup_base`. Installs the base requirements.
    """
    if distro == "arch":
        from fabric_colors.distro.arch import _server_base
        _server_base()


@task
@set_target_env
def setup_python(distro="arch"):
    """
    Usage: `fab -R all server.setup_python`. Sets up the python environment
    """
    if distro == "arch":
        from fabric_colors.distro.arch import _server_python_arch, \
                _server_virtualenvwrapper_arch
        _server_python_arch()
        _server_virtualenvwrapper_arch(env.user, systemwide=True)
        _server_virtualenvwrapper_arch(env.user)


@task
@set_target_env
def chk_exists(path):
    """
    Usage: `fab -R dev server.chk_exists:path`. Returns 1 or empty string.
    """
    cmd = """if [ -e "{0}" ]; then echo 1; else echo ""; fi""".format(path)
    return run(cmd)


@task
@set_target_env
def get_ownership(path):
    """
    Usage: `fab -R all server.get_ownership`. Given a path, and the target node, return owner and group for that directory
    """
    owner = None
    group = None
    if chk_exists(path):
        cmd = "ls -ld %s | awk \'{print $3}\'" % path
        cmd2 = "ls -ld %s | awk \'{print $4}\'" % path
        owner = run(cmd)
        group = run(cmd2)
    return owner, group


def show_sudo_users_and_groups(ug, nopasswd):
    """
    Helper function that prints out users and groups with sudo (or no passwd sudo) rights.
    """
    ug_users = []
    ug_groups = []

    nopasswd_string = ""
    if nopasswd:
        nopasswd_string = "no password "

    if not ug:
        print(red("There are no users or groups with {0}sudo rights.".format(nopasswd_string)))
        return ug_users, ug_groups

    for item in ug:
        if item[0] == "%":
            ug_groups.append(item[1:])
        else:
            ug_users.append(item)

    if ug_users:
        print(green("Users with {0}sudo rights:".format(nopasswd_string)))
        print(cyan(ug_users))
    else:
        print(red("No users with {0}sudo rights".format(nopasswd_string)))

    if ug_groups:
        print(green("Groups with {0}sudo rights:".format(nopasswd_string)))
        print(cyan(ug_groups))
    else:
        print(red("No groups with {0}sudo rights".format(nopasswd_string)))

    print("\n")  # just formatting
    return ug_users, ug_groups


@task
@set_target_env
def sudo_users_and_groups(nopasswd=False):
    """
    Usage: `fab -R dev server.sudo_users_and_groups:nopasswd`. nopasswd(optional)=True/False.
    """
    env.user = "root"
    nopasswd_string = ""
    nopasswd_string2 = ""
    if nopasswd:
        nopasswd_string = "NOPASSWD: "
        nopasswd_string2 = "no password "

    print(magenta("Retrieving users and groups with {0}sudo rights".format(nopasswd_string2)))

    ug = run("""
        line="ALL=(ALL) {0}ALL";
        result=$(grep -v "#" /etc/sudoers | grep '{0}ALL$' | sed "s/$line//g");
        echo $result;
    """.format(nopasswd_string)).split()

    return show_sudo_users_and_groups(ug, nopasswd)


@task
@set_target_env
def usersudo(user=env.user, sudogroup="sudo"):
    """
    Usage: `fab -R dev server.usersudo:user,sudogroup`. Adds deploying user to the given sudo group.
    """
    ug_users, ug_groups = sudo_users_and_groups()
    if not ug_groups:
        print(magenta("No sudo groups yet, so we will enable the (given) sudo group ") + cyan("{0}".format(sudogroup)) + magenta("."))
        visudo(sudogroup)
        ug_users, ug_groups = sudo_users_and_groups()

    if sudogroup in ug_groups:
        print(green("Adding our user into the sudo group"))
        run("gpasswd -a {0} {1}".format(user, sudogroup))
    else:
        print(red("Something went wrong and we could not add your deploying user to the sudo group {0}.".format(sudogroup)))


@task
@set_target_env
def initializers():
    """
    Shows us which are the services that will be initialized automatically after a reboot.
    """
    cmd = """ls /etc/systemd/system/*.wants/ | grep -v "/etc/systemd/system" """
    results = run(cmd).split()
    return results
