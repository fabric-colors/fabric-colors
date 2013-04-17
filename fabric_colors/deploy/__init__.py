__all__ = ['deploy', 'mkvirtualenv', 'releases_list', 'releases_cleanup', 'pip_requirements']

import subprocess

from fabric.api import env, run, sudo, task
from fabric.colors import green, cyan, red

from fabric.context_managers import prefix
from fabric_colors.environment import _env_set, set_target_env
from fabric_colors.deploy.git import git_branch_check, git_archive_and_upload_tar
from fabric_colors.deploy.releases import cleanup as _releases_cleanup, symlink_current
from fabric_colors.utilities.django_conventions import django_collectstatic
from fabric_colors.utilities.emails import email_on_success
from fabric_colors.utilities import chk_req


@task
@set_target_env
def test_host_check():
    """
    Usage: `fab -R all deploy.test_host_check` or `fab -H mysite.com deploy.test_host_check`
    """
    if env.test:
        print(green("Target host") + cyan(" {0} ".format(env.host)) + green("is designated as a test host."))
        print("This means that we can deploy to it from any git branch.")
    else:
        print(green("Target host") + cyan(" {0} ".format(env.host)) + green("is ") + red("NOT ") + green("designated as a test host."))
        print("This means that we can only deploy to this node from our master git branch.")
    return env.test


@task(default=True)
@set_target_env
def deploy(email=False):
    """
    Usage: `fab -R all deploy` or fab -H mysite.com deploy`. Execute a deployment to the given groups of hosts or host
    """
    if not chk_req():
        return

    if git_branch_check() or test_host_check():
        release()
        git_archive_and_upload_tar()
        pip_requirements()
        django_collectstatic(deploy=True)
        symlink_current()
        _releases_cleanup()
        email_on_success(trigger=email)


def release():
    env.release = str(subprocess.Popen(["git", "rev-parse", "--short", "HEAD"], \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()
    print(env.release)


@task
@set_target_env
def mkvirtualenv():
    """
    Usage: `fab -R all mkvirtualenv`. Create the virtualenv for our project on the target machine.
    """
    run('mkvirtualenv -p python2.7 --distribute %s' % (env.virtualenv))


def prepare_deploy_env(target):
    """
    Make sure that we have the release directories before executing deployment.
    """
    _env_set(target)
    result = run('; if [ -d "{0}" ]; then echo 1; else echo ""; fi'.format(env.path_releases))
    print result.stdout
    if not result.stdout:
        sudo('; mkdir -p {0}'.format(env.path_releases))
        sudo('; chown {0}:{0} -R {1}'.format(env.user, env.path))
    else:
        print("{0} already exists".format(env.path_releases))


@task
@set_target_env
def pip_requirements():
    """
    Usage: `fab -R all deploy.pip_requirements`. Install the required python packages from the requirements.txt file using pip
    """
    result = None
    if not env.get('release'):
        release()
    with prefix(env.activate):
        result = run('pip install -r %(path)s/releases/%(release)s/requirements.txt' % env)

    if not result:
        print(red("pip install failed. Please manually debug the dependencies and compilation problem."))
        exit()
