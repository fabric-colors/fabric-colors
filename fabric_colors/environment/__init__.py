import os
import subprocess
from functools import wraps

from fabric.api import env, run
from fabric.context_managers import hide
from fabric.operations import local
from fabric.colors import green, red

import fabsettings


def _env_set(target):
    """
    Grab environment variables given the target machine and assign it to fabric's env
    """
    if target == 'vagrant':
        # vagrant specific settings
        env.run = run
        env.user = 'vagrant'
        raw_ssh_config = subprocess.Popen(["vagrant", "ssh-config"], stdout=subprocess.PIPE).communicate()[0]
        ssh_config = dict([l.strip().split() for l in raw_ssh_config.split("\n") if l])
        env.user = ssh_config["User"]
        env.hosts = ["127.0.0.1:%s" % (ssh_config["Port"])]
        env.host_string = env.hosts[0]    # We need to explicitly specify this for sudo and run.
        env.key_filename = ssh_config["IdentityFile"]
        return True
    elif target == 'localhost':
        # all environment variables relating to a developer's localhost
        env.run = local
        env.target = 'local'  # By convention, we set our settings for localhost to be local.py
        env.user = env.local_user
        env.project_home = os.getenv("PROJECT_HOME")
        env.project_path = '%(project_home)s/%(project_name)s' % env
        env.virtualenv = fabsettings.PROJECT_SITES.get('localhost', {}).get('VIRTUALENV', env.project_name)
        env.activate = 'source ~/.bash_profile; source `which virtualenvwrapper.sh`; workon {0}'.format(env.virtualenv)
        return True
    elif target not in list(env.project_sites.viewkeys()):
        # handle environment that isn't specified
        print(red("Oops. There's no such node."))
        if list(env.project_sites.viewkeys()):
            print(green("Your specified nodes are:"))
            for node in list(env.project_sites.viewkeys()):
                print(green(node) + ": " + green(env.project_sites[node]))
        else:
            print(red("You don't have any nodes configured in your fabsettings' PROJECT_SITES yet"))
        return None

    # handle environment that was specified
    env.run = run
    env.target = target
    env.user = fabsettings.PROJECT_SITES[target].get('USER', 'web')
    env.group = fabsettings.PROJECT_SITES[target].get('GROUP', env.user)
    env.hosts = [env.project_sites[target]['NAME']]
    env.host_string = env.hosts[0]
    env.path = fabsettings.PROJECT_SITES[target].get('PATH', '/var/www/%s/%s' % (target, env.project_name))
    env.path_releases = fabsettings.PROJECT_SITES[target].get('PATH_RELEASES', '/var/www/%s/%s/releases' % (target, env.project_name))
    env.path_release_current = fabsettings.PROJECT_SITES[target].get('PATH_RELEASE_CURRENT', '/var/www/%s/%s/releases/current' % (target, env.project_name))
    env.project_path = '%(path_release_current)s/%(project_name)s' % env  # slash prepended
    env.virtualenv = fabsettings.PROJECT_SITES[target].get('VIRTUALENV', env.project_name)
    env.activate = 'source ~/.bash_profile; source `which virtualenvwrapper.sh`; workon {0}'.format(env.virtualenv)
    env.webserver_type = fabsettings.PROJECT_SITES[target].get('WEBSERVER', {}).get('TYPE', 'uwsgi')
    env.webserver_port = fabsettings.PROJECT_SITES[target].get('WEBSERVER', {}).get('PORT', '3030')
    env.test = env.project_sites[target].get('TEST', False)
    env.newrelic = fabsettings.PROJECT_SITES[target].get('NEW_RELIC', False)
    env.newrelic_program = ""
    if env.newrelic:
        env.newrelic_program = 'NEW_RELIC_CONFIG_FILE={0}/{1} newrelic-admin run-program '.\
                                format(env.path_release_current, env.newrelic.get('INI_FILE', 'newrelic.ini'))

    return True


def _env_set_distro():
    # Set env.distro

    with hide('running', 'stdout'):
        if env.run == local:
            name = local('uname -s', capture=True)
        else:
            name = env.run('uname -s')

        env.distro = None
        if name == "Darwin":
            env.distro = "mac"
        elif name == "Linux":
            result = env.run('cat /etc/*-release')
            import re
            result_list = re.findall(r'([^=\s,]+)=([^=\s,]+)', result)
            for item in result_list:
                if item[0] == 'ID':
                    env.distro = item[1]
                    return env.distro

    return env.distro


def set_target_env(f):
    """
    decorator function that dynamically sets the current host's env variables
    using _env_set(target)

    Usage on a fabric function:
        @set_target_env
        def host_type():
            run('uname -s')
    """
    @wraps(f)
    def wrapper(*args, **kwargs):
        if env.host == "localhost":
            _env_set("localhost")
        for key, value in fabsettings.PROJECT_SITES.iteritems():
            # key is the identifier, e.g. "dev", "prod", etc etc
            for k, v in value.iteritems():
                if v == env.host:
                    # iterate in the nested dictionary
                    # if the nested dictionary's name is equivalent to env.host
                    # we will set our global state env with _env_set(key)
                    _env_set(key)

        if not env.get('distro'):
            _env_set_distro()
        return f(*args, **kwargs)
    return wrapper
