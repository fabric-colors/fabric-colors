__all__ = ['deploy', 'mkvirtualenv', 'releases_list', 'releases_cleanup']

import re
import subprocess

from fabric.api import env, run, sudo, require
from fabric.context_managers import prefix, cd, hide, settings as fabconfig
from fabric_colors.environment import _env_get
from fabric_colors.deployment.git import git_branch_check, git_archive_and_upload_tar
from fabric_colors.utilities.django_conventions import django_collectstatic
from fabric_colors.utilities.emails import email_on_success
from fabric_colors.utilities import chk_req

import fabsettings


def test_node_check(target):
    print "Target node %s is designated as a test node." % target
    print "This means that we can deploy to it from any git branch."
    return env.test


def deploy(target, email=False):
    """
    Usage: `fab deploy:dev`. Execute a deployment to the given target machine.
    """
    _env_get(target)
    env.release = str(subprocess.Popen(["git", "rev-parse", "--short", "HEAD"], \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()

    if not chk_req():
        return

    if git_branch_check() or test_node_check(target):
        git_archive_and_upload_tar(target)
        pip_install_requirements(target)
        django_collectstatic(target, deploy=True)
        symlink_current_release()
        releases_cleanup(target)
        email_on_success(target, trigger=email)


def mkvirtualenv(target):
    """
    Create the virtualenv for our project on the target machine. `fab mkvirtualenv:dev`
    """
    _env_get(target)
    run('mkvirtualenv -p python2.7 --distribute %s' % (env.virtualenv))


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


def pip_install_requirements(target):
    """
    Install the required python packages from the requirements.txt file using pip
    """
    _env_get(target)
    require('release', provided_by=[deploy])
    with prefix(env.activate):
        run('&& pip install -r %(path)s/releases/%(release)s/requirements.txt' % env)


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


def releases_list(target, show=True):
    """
    Returns a list of deploy directories.
    """
    _env_get(target)
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
        print("Number of release directories on {0} = {1}".format(target, num))
        if show == True:
            print(result_list)
        return result_list, num


def releases_cleanup(target, n=None):
    """
    Ensure that target node only has `n` most recent deployed directories, where `n` by default is 10 but can be overridden by that node's settings in fabsettings.
    """
    if n:
        # If user provides n, we will override our fabsettings/default attributes and use user-provided value
        n = int(n)
    else:
        # Otherwise, we will use what we have in fabsettings or default to 10
        n = fabsettings.PROJECT_SITES[target].get('NUM_RELEASES', 10)

    if n <= 2:
        print("'n' must be 2 or more")
        return

    result_list, num = releases_list(target)
    if num <= n:
        print("Only {0} release directories on {1} at the moment. Which is already less than or equal to what you want to trim to: {2}".format(num, target, n))
        return

    _env_get(target)
    total_to_trim = num - n
    print("Trimming release directories from {0} to {1} on {2}".format(total_to_trim, n, target))
    print("A total of {0} release directories will be deleted".format(total_to_trim))
    with cd(env.path_releases):
        cmd = "ls -1tr | grep -v '{0}*' | grep -v 'current' | head -n {1} | xargs -d '\\n' rm -rf".format(fabsettings.PROJECT_NAME, total_to_trim)
        run(cmd)
    releases_list(target, False)
