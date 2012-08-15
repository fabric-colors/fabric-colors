from fabric_colors.deployment import _env_get
from fabric.api import env


def info(target="localhost"):
    """
    Show the details relating to the current project, given an optional machine target (defaults to "localhost" if not provided). e.g. `fab info:dev`
    """
    try:
        from django.conf import settings
        from fabsettings import PROJECT_NAME, PROJECT_SITES
        print("Running with PROJECT_ROOT {0}".format(settings.PROJECT_ROOT))
        print("Our PROJECT_NAME is {0}".format(PROJECT_NAME))
        print("We currently have the following instances:")
        for item in PROJECT_SITES:
            print " * %s \n" % item
        _env_get(target)
        print("This is the environment details on {0}".format(target))
        print env
    except:
        print "This is not a django project"
