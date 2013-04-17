import subprocess
import fabsettings

from fabric.api import env, run, local, sudo, task
from fabric.contrib.project import rsync_project

from fabric_colors.environment import set_target_env
from fabric_colors.distro import get_ownership


@task
@set_target_env
def git_branch_check():
    """
    Usage: `fab -R all deploy.git_branch_check`. Check that we are on master branch before permitting deploy
    """
    cmd = 'git branch | grep "*" | sed "s/* //"'
    current_branch = str(subprocess.Popen(cmd, \
            shell=True,\
            stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()
    env.git_branch = current_branch
    if env.git_branch == "master":
        return True
    else:
        return False


@task
@set_target_env
def git_archive_and_upload_tar():
    """
    Create an archive from the current git branch and upload it to target machine.
    """
    cmd = 'git branch | grep "*" | sed "s/* //"'
    current_branch = str(subprocess.Popen(cmd, \
            shell=True,\
            stdin=subprocess.PIPE, \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()
    env.git_branch = current_branch
    local('git archive --format=tar %(git_branch)s > %(release)s.tar' % env)
    local('touch `git describe HEAD`-`git config --get user.email`.tag')
    local('tar rvf %(release)s.tar `git describe HEAD`-`git config --get user.email`.tag; \
            rm `git describe HEAD`-`git config --get user.email`.tag' % env)
    local('gzip %(release)s.tar' % env)
    current_owner, current_group = get_ownership(env.path, env.target)
    deploying_user = fabsettings.PROJECT_SITES[env.target].get('USER', 'web')
    deploying_group = fabsettings.PROJECT_SITES[env.target].get('GROUP', deploying_user)
    if current_owner != deploying_user:
        print("Problem Houston. Our root path {0} for deployments is not owned by our deploying user {1}.".format(env.path, deploying_user))
        print("Attempting to set the correct ownership permissions before proceeding.")
        sudo("sudo chown -R {0}:{1} {2}".format(deploying_user, deploying_group, env.path))
    run('; mkdir -p %(path)s/releases/%(release)s' % env)
    run('; mkdir -p %(path)s/packages/' % env)
    rsync_project('%(path)s/packages/' % env, '%(release)s.tar.gz' % env, extra_opts='-avz --progress')
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env)
    local('rm %(release)s.tar.gz' % env)
