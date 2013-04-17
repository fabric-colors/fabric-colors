__all__ = ['deploy', 'mkvirtualenv', 'releases_list', 'releases_cleanup', 'pip_install_requirements']

import re
import subprocess

from fabric.api import env, run, sudo, require, task
from fabric.colors import green, cyan, red

from fabric.context_managers import prefix, cd, hide, settings as fabconfig
from fabric_colors.environment import _env_set, set_target_env
from fabric_colors.deploy.git import git_branch_check, git_archive_and_upload_tar
from fabric_colors.utilities.django_conventions import django_collectstatic
from fabric_colors.utilities.emails import email_on_success
from fabric_colors.utilities import chk_req

import fabsettings


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
        pip_install_requirements()
        django_collectstatic(deploy=True)
        symlink_current_release()
        releases_cleanup()
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
def pip_install_requirements():
    """
    Install the required python packages from the requirements.txt file using pip
    """
    result = None
    if not env.get('release'):
        release()
    with prefix(env.activate):
        result = run('pip install -r %(path)s/releases/%(release)s/requirements.txt' % env)

    if not result:
        print(red("pip install failed. Please manually debug the dependencies and compilation problem."))
        exit()


def symlink_current_release():
    """
    Symlink our current release
    """
    require('release', provided_by=[deploy])
    with cd(env.path_releases):
        if symlink_check():
            run('rm current; ln -s %(release)s current' % env)
            print('Removed current symlink and pointing at new release %(release)s.' % env)
        else:
            run('ln -s %(release)s current' % env)
            print('Pointing at new release %(release)s.' % env)


def symlink_check():
    """
    Check the hash pointing to the current symlink
    """
    with cd(env.path_releases):
        print('Current release is %(release)s' % env)
        cmd = "[ -d current ] && echo '1'"
        with fabconfig(hide('everything'), warn_only=True):
            result = run(cmd)
            return result


@task
@set_target_env
def releases_list(show=True):
    """
    Usage: `fab -R all releases_list`. Returns a list of deploy directories.
    """
    with cd(env.path_releases):
        cmd = "ls -tm ."
        result = run(cmd)
        result_list = result.split(",")
        result_list = [item.strip() for item in result_list]  # clean up whitespaces
        if not fabsettings.PROJECT_NAME:
            print("Please define your PROJECT_NAME in fabsettings.py")

        # Exclude 'current' symlink and directories starting with the same
        # project_name
        result_list[:] = [item for item in result_list if item != 'current']
        result_list[:] = [item for item in result_list if not re.match(fabsettings.PROJECT_NAME, item)]

        num = len(result_list)
        print("Number of release directories on {0} = {1}".format(env.target, num))
        if show == True:
            print(result_list)
        return result_list, num


@task
@set_target_env
def releases_cleanup(n=None):
    """
    Usage: `fab -R all releases_cleanup`. Ensure that target node only has `n` most recent deployed directories,
    where `n` by default is 10 but can be overridden by that node's settings in fabsettings.
    """
    if n:
        # If user provides n, we will override our fabsettings/default attributes and use user-provided value
        n = int(n)
    else:
        # Otherwise, we will use what we have in fabsettings or default to 10
        n = fabsettings.PROJECT_SITES[env.target].get('NUM_RELEASES', 10)

    if n <= 2:
        print("'n' must be 2 or more")
        return

    result_list, num = releases_list(env.target)
    if num <= n:
        print("Only {0} release directories on {1} at the moment. Which is already less than or equal to what you want to trim to: {2}".format(num, env.target, n))
        return

    total_to_trim = num - n
    print("Trimming release directories from {0} to {1} on {2}".format(total_to_trim, n, env.target))
    print("A total of {0} release directories will be deleted".format(total_to_trim))
    with cd(env.path_releases):
        cmd = "ls -1tr | grep -v '{0}*' | grep -v 'current' | head -n {1} | xargs -d '\\n' rm -rf".format(fabsettings.PROJECT_NAME, total_to_trim)
        run(cmd)
    releases_list(False)
