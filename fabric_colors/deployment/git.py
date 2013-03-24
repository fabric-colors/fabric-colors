import subprocess

from fabric.api import env, run, local
from fabric.contrib.project import rsync_project

from fabric_colors.environment import _env_get


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
    _env_get(target)
    run('; mkdir -p %(path)s/releases/%(release)s' % env)
    run('; mkdir -p %(path)s/packages/' % env)
    rsync_project('%(path)s/packages/' % env, '%(release)s.tar.gz' % env, extra_opts='-avz --progress')
    run('cd %(path)s/releases/%(release)s && tar zxf ../../packages/%(release)s.tar.gz' % env)
    local('rm %(release)s.tar.gz' % env)
