__all__ = ['info', 'django_create_public', 'django_makemessages',
'django_collectstatic', 'django_compilemessages', 'postgres_backup',
'media_backup', 'chk_req']

import subprocess
from pprint import pprint

from fabric_colors.deployment import _env_set
from fabric.api import env

from fabric_colors.utilities.django_conventions import (django_collectstatic,
        django_create_public, django_compilemessages, django_makemessages)
from fabric_colors.utilities.backups import (postgres_backup, media_backup)


PROJECT_NAME = env.project_name
PROJECT_SITES = env.project_sites


def info(target="localhost"):
    """
    Usage: `fab info:dev`. Show the details relating to the current project,
    given an optional machine target (defaults to "localhost" if not provided).
    """
    try:
        print("Our PROJECT_NAME is {0}".format(PROJECT_NAME))
        print("We currently have the following instances:")
        for k, v in PROJECT_SITES.iteritems():
            print " * {0} {1}".format(k, v)
        _env_set(target)
        print("\n")
        print("This is the environment details on {0}".format(target))
        pprint(env)
    except:
        print "This is not a django project"


def chk_req():
    """
    Usage `fab chk_req`. Check if the current requirements.txt file matches what is in user's virtualenv. Returns True or False.
    """
    _env_set("localhost")
    env.warn_only = True
    path_to_req = env.project_path + "/requirements.txt"
    cmd = "/bin/bash -c 'diff -B <(sort {0}) <(pip freeze | sort)'".format(path_to_req)
    result = str(subprocess.Popen(cmd, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE).communicate()[0]).rstrip()
    result_list = result.splitlines()
    mismatch_dependencies = [item[1:].strip() if item[0] == ">" else None for item in result_list]
    mismatch_dependencies = filter(None, mismatch_dependencies)
    if mismatch_dependencies:
        for item in mismatch_dependencies:
            print(item + " is not in your requirements file.")
        print("Please run pip freeze to update your requirements file.")
        return False
    else:
        return True
