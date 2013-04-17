import re

from fabric.api import task, env, run
from fabric.context_managers import cd, hide, settings as fabconfig

from fabric_colors.environment import set_target_env

import fabsettings


@task
@set_target_env
def showlist(show=True):
    """
    Usage: `fab -R all releases.showlist`. Returns a list of deploy directories.
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
def cleanup(n=None):
    """
    Usage: `fab -R all releases.cleanup`. Ensure that target node only has `n` most recent deployed directories,
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

    result_list, num = showlist(env.target)
    if num <= n:
        print("Only {0} release directories on {1} at the moment. Which is already less than or equal to what you want to trim to: {2}".format(num, env.target, n))
        return

    total_to_trim = num - n
    print("Trimming release directories from {0} to {1} on {2}".format(total_to_trim, n, env.target))
    print("A total of {0} release directories will be deleted".format(total_to_trim))
    with cd(env.path_releases):
        cmd = "ls -1tr | grep -v '{0}*' | grep -v 'current' | head -n {1} | xargs -d '\\n' rm -rf".format(fabsettings.PROJECT_NAME, total_to_trim)
        run(cmd)
    showlist(False)


@task
@set_target_env
def symlink_current():
    """
    Usage: `fab -R all releases.symlink_current`. Symlink our current release.
    """
    with cd(env.path_releases):
        if symlink_check():
            run('rm current; ln -s %(release)s current' % env)
            print('Removed current symlink and pointing at new release %(release)s.' % env)
        else:
            run('ln -s %(release)s current' % env)
            print('Pointing at new release %(release)s.' % env)


@task
@set_target_env
def symlink_check():
    """
    Usage: `fab -R all releases.symlink_check`. Check the hash pointing to the current symlink.
    """
    with cd(env.path_releases):
        print('Current release is %(release)s' % env)
        cmd = "[ -d current ] && echo '1'"
        with fabconfig(hide('everything'), warn_only=True):
            result = run(cmd)
            return result
