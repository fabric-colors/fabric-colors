import os
import subprocess

from fabric.api import env
import fabsettings


def _env_get(target):
    """
    Grab environment variables given the target machine and assign it to fabric's env
    """
    if target == 'vagrant':
        # vagrant specific settings
        env.user = 'vagrant'
        raw_ssh_config = subprocess.Popen(["vagrant", "ssh-config"], stdout=subprocess.PIPE).communicate()[0]
        ssh_config = dict([l.strip().split() for l in raw_ssh_config.split("\n") if l])
        env.user = ssh_config["User"]
        env.hosts = ["127.0.0.1:%s" % (ssh_config["Port"])]
        env.host_string = env.hosts[0]    # We need to explicitly specify this for sudo and run.
        env.key_filename = ssh_config["IdentityFile"]
        return
    elif target == 'localhost':
        # all environment variables relating to a developer's localhost
        env.project_home = os.getenv("PROJECT_HOME")
        env.project_path = '%(project_home)s/%(project_name)s' % env
        env.user = env.local_user
        return
    elif target not in list(env.project_sites.viewkeys()):
        # handle environment that isn't specified
        print ("Oops. There's no such site. try `fab _env_get:dev` or `fab env_get:prod`")
        return

    # handle environment that was specified
    env.user = 'web'
    env.hosts = [env.project_sites[target]['NAME']]
    env.host_string = env.hosts[0]
    env.path = fabsettings.PROJECT_SITES[target].get('PATH', '/var/www/%s/%s' % (target, env.project_name))
    env.path_releases = fabsettings.PROJECT_SITES[target].get('PATH_RELEASES', '/var/www/%s/%s/releases' % (target, env.project_name))
    env.path_release_current = fabsettings.PROJECT_SITES[target].get('PATH_RELEASE_CURRENT', '/var/www/%s/%s/releases/current' % (target, env.project_name))
    env.project_path = '%(path_release_current)s/%(project_name)s' % env  # slash prepended
    env.test = env.project_sites[target].get('TEST', False)
