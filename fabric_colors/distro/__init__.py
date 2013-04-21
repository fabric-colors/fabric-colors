from fabric.api import task, env
from fabric.colors import green, red

from fabric_colors.environment import set_target_env


@task
@set_target_env
def distro():
    """
    Usage: `fab -R all distro`. Determine the distro of given target host(s).
    """
    if env.get('distro'):
        print(green("Host distro is {0}.".format(env.distro)))
    else:
        print(red("Unable to determine host's distro."))
