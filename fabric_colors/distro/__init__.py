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
