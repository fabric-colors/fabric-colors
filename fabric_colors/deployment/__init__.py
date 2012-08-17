import os
import subprocess

from fabric.api import env, run, sudo, require, local
from fabric.context_managers import prefix, cd, hide, settings as fabconfig
from fabric.contrib.project import rsync_project
from fabric_colors.deployment import *


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
    env.path = '/var/www/%s/%s' % (target, env.project_name)
    env.path_releases = '/var/www/%s/%s/releases' % (target, env.project_name)
    env.path_release_current = '/var/www/%s/%s/releases/current' % (target, env.project_name)
    env.project_path = '%(path_release_current)s/%(project_name)s' % env  # slash prepended


def deploy(target):
    """
    Execute a deployment to the given target machine. `fab deploy:dev`
    """
    _env_get(target)
    env.release = str(subprocess.Popen(["git", "rev-parse", "--short", "HEAD"], \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()
    if git_branch_check():
        git_archive_and_upload_tar()
        pip_install_requirements()
        symlink_current_release()
        django_collectstatic(target)


def mkvirtualenv(target):
    """
    Create the virtualenv for our project on the target machine. `fab mkvirtualenv:dev`
    """
    _env_get(target)
    run('mkvirtualenv -p python2.7 %s' % (env.project_name))


def prepare_deploy_env(target):
    """
    Make sure that we have the release directories before executing deployment.
    """
    _env_get(target)
    result = run('; if [ -d "{0}" ]; then echo 1; else echo ""; fi'.format(env.path_releases))
    print result.stdout
    if not result.stdout:
        sudo('; mkdir -p {0}'.format(env.path_releases))
        sudo('; chown {0}:{0} -R {1}'.format(env.user, env.path))
    else:
        print("{0} already exists".format(env.path_releases))


def git_branch_check():
    require('release', provided_by=[deploy])
    current_branch = str(subprocess.Popen('git branch | grep "*" | sed "s/* //"', \
            shell=True,\
            stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()
    env.git_branch = current_branch
    if env.git_branch == "master":
        return True
    else:
        print("You are currently in the %(git_branch)s branch so `fab deploy:your_target` will not work." % env)
        print("Please checkout to master branch and merge your features before running `fab deploy:your_target`.")
        return False


def git_archive_and_upload_tar():
    """
    Create an archive from the current git branch and upload it to target machine.
    """
    require('release', provided_by=[deploy])
    current_branch = str(subprocess.Popen('git branch | grep "*" | sed "s/* //"', \
            shell=True,\
            stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()
    env.git_branch = current_branch
    local('git archive --format=tar %(git_branch)s | gzip > %(release)s.tar.gz' % env)
    run('mkdir -p %(path)s/releases/%(release)s' % env)
    run('mkdir -p %(path)s/packages/' % env)
    rsync_project('%(path)s/packages/' % env, '%(release)s.tar.gz' % env, extra_opts='-avz --progress')
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env)
    local('rm %(release)s.tar.gz' % env)


def pip_install_requirements():
    """
    Install the required python packages from the requirements.txt file using pip
    """
    require('release', provided_by=[deploy])
    with prefix(env.activate):
        run('&& pip install -r %(path)s/releases/%(release)s/requirements.txt' % env)


def django_collectstatic(target):
    _env_get(target)
    with prefix(env.activate):
        with cd(env.path_release_current):
            if target == "dev" or target == "prod":
                run("python manage.py collectstatic --noinput --settings=%s.settings.%s" % (env.project_name, target))
            else:
                run("python manage.py collectstatic --noinput")


def symlink_current_release():
    """
    Symlink our current release
    """
    require('release', provided_by=[deploy])
    with cd(env.path):
        if symlink_check():
            run('cd releases; rm current; ln -s %(release)s current' % env)
        else:
            run('cd releases; ln -s %(release)s current' % env)


def symlink_check():
    with cd(env.path):
        cmd = "cd releases; [ -d current ] && echo '1'"
        with fabconfig(hide('everything'), warn_only=True):
            return bool(run(cmd))
