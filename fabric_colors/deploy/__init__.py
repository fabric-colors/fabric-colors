import re

from fabric.api import env, run, sudo, task
from fabric.colors import green, cyan, red

from fabric.context_managers import prefix
from fabric_colors.environment import _env_set, set_target_env
from fabric_colors.deploy.git import git_branch_check, git_archive_and_upload_tar
from fabric_colors.deploy.releases import cleanup as _releases_cleanup, symlink_current, manage_release
from fabric_colors.webserver import webserver
from fabric_colors.virtualenv import chkvirtualenv, mkvirtualenv
from fabric_colors.utilities.django import collectstatic
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
        manage_release('Deployment start')
        git_archive_and_upload_tar()
        pip_requirements()
        collectstatic(deploy=True)
        # TODO:
        # automatically run migration; once successful,
        # conclude the deployment with symlink_current()
        symlink_current()
        webserver()
        # post-deployment tasks
        manage_release('Deployment start')
        _releases_cleanup()
        email_on_success(trigger=email)


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


@set_target_env
def pip_package_preinstall():
    """
    Preinstall packages listed in package_exceptions if they are found in requirements.txt!
    Packages listed in package_exceptions need to have their setup.py executed beforehand.
    """
    package_preinstall = []
    package_exceptions = ['numpy', 'uWSGI']  # Allow user to specify this in fabsettings
    packages = open('requirements.txt').read().splitlines()
    for e in package_exceptions:
        for package in packages:
            if re.match(e, package):
                package_preinstall.append(package)

    for p in package_preinstall:
        run('pip install {0}'.format(p))


@task
@set_target_env
def pip_requirements():
    """
    Usage: `fab -R all deploy.pip_requirements`. Install the required python packages from the requirements.txt file using pip
    """
    result = None
    if not env.get('release'):
        manage_release(disable_newrelic=True)

    if not chkvirtualenv():
        mkvirtualenv()

    with prefix(env.activate):
        pip_package_preinstall()
        result = run('pip install -r %(path)s/releases/%(release)s/requirements.txt' % env)

    if not result:
        print(red("pip install failed. Please manually debug the dependencies and compilation problem."))
        exit()
