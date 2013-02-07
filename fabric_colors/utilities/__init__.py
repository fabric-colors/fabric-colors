__all__ = ['info', 'django_create_public', 'django_collectstatic', 'django_compilemessages']

from fabric_colors.deployment import _env_get
from fabric.api import env

from fabric_colors.utilities.django_conventions import \
        django_collectstatic, django_create_public, django_compilemessages

PROJECT_NAME = env.project_name
PROJECT_SITES = env.project_sites


def info(target="localhost"):
    """
    Usage: `fab info:dev`. Show the details relating to the current project, given an optional machine target (defaults to "localhost" if not provided).
    """
    try:
        print("Our PROJECT_NAME is {0}".format(PROJECT_NAME))
        print("We currently have the following instances:")
        for k, v in PROJECT_SITES.iteritems():
            print " * {0} {1}".format(k, v)
        _env_get(target)
        print("\n")
        print("This is the environment details on {0}".format(target))
        print env
    except:
            print "This is not a django project"
