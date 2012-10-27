import os

from fabric_colors.deployment import _env_get
from fabric.api import env

PROJECT_NAME = env.project_name
PROJECT_SITES = env.project_sites


def info(target="localhost"):
    """
    Show the details relating to the current project, given an optional machine target (defaults to "localhost" if not provided). e.g. `fab info:dev`
    """
    try:
        from django.conf import settings
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
