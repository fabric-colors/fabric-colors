__all__ = ['deploy', 'mkvirtualenv']

import subprocess

from fabric.api import env, run, sudo, require
from fabric.context_managers import prefix, cd, hide, settings as fabconfig
from fabric_colors.environment import _env_get
from fabric_colors.deployment.git import git_branch_check, git_archive_and_upload_tar
from fabric_colors.utilities.django_conventions import django_collectstatic


def deploy(target):
    """
    Usage: `fab deploy:dev`. Execute a deployment to the given target machine.
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
    run('mkvirtualenv -p python2.7 --distribute %s' % (env.project_name))


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


def pip_install_requirements():
    """
    Install the required python packages from the requirements.txt file using pip
    """
    require('release', provided_by=[deploy])
    with prefix(env.activate):
        run('&& pip install -r %(path)s/releases/%(release)s/requirements.txt' % env)


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
    """
    Check the hash pointing to the current symlink
    """
    with cd(env.path):
        cmd = "cd releases; [ -d current ] && echo '1'"
        with fabconfig(hide('everything'), warn_only=True):
            return bool(run(cmd))
