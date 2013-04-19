from fabric.api import task, run, env

from fabric_colors.environment import set_target_env


@task
@set_target_env
def mkvirtualenv():
    """
    Usage: `fab -R all mkvirtualenv`. Create the virtualenv for our project on the target machine.
    """
    run('mkvirtualenv --distribute %s' % (env.virtualenv))


@task
@set_target_env
def chkvirtualenv():
    """
    Usage: `fab -R dev chkvirtualenv`. Check that we have the virtualenv for our project on the target machine.
    """
    results = lsvirtualenv()
    if env.virtualenv in results:
        return True
    return False


@task
@set_target_env
def lsvirtualenv():
    """
    Usage: `fab -R dev lsvirtualenv`. List all virtualenvs.
    """
    results = run('lsvirtualenv').split()
    return results


@task
@set_target_env
def rmvirtualenv(name):
    """
    Usage: `fab -R dev rmvirtualenv:name_of_virtualenv`.
    """
    run('rmvirtualenv {0}'.format(name))
