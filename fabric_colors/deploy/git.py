import subprocess
import fabsettings

from fabric.api import env, run, local, sudo, task
from fabric.contrib.project import rsync_project

from fabric_colors.environment import _env_set
from fabric_colors.distro import get_ownership


def git_branch_check():
    """
    Check that we are on master branch before permitting deploy
    """
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


@task
def git_archive_and_upload_tar(target):
    """
    Create an archive from the current git branch and upload it to target machine.
    """
    current_branch = str(subprocess.Popen('git branch | grep "*" | sed "s/* //"', \
            shell=True,\
            stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()
    env.git_branch = current_branch
    local('git archive --format=tar %(git_branch)s > %(release)s.tar' % env)
    local('touch `git describe HEAD`-`git config --get user.email`.tag')
    local('tar rvf %(release)s.tar `git describe HEAD`-`git config --get user.email`.tag; \
            rm `git describe HEAD`-`git config --get user.email`.tag' % env)
    local('gzip %(release)s.tar' % env)
    _env_set(target)
    current_owner, current_group = get_ownership(env.path, target)
    deploying_user = fabsettings.PROJECT_SITES[target].get('USER', 'web')
    deploying_group = fabsettings.PROJECT_SITES[target].get('GROUP', deploying_user)
    if current_owner != deploying_user:
        print("Problem Houston. Our root path {0} for deployments is not owned by our deploying user {1}.".format(env.path, deploying_user))
        print("Attempting to set the correct ownership permissions before proceeding.")
        sudo("sudo chown -R {0}:{1} {2}".format(deploying_user, deploying_group, env.path))
    run('; mkdir -p %(path)s/releases/%(release)s' % env)
    run('; mkdir -p %(path)s/packages/' % env)
    rsync_project('%(path)s/packages/' % env, '%(release)s.tar.gz' % env, extra_opts='-avz --progress')
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env)
    local('rm %(release)s.tar.gz' % env)
