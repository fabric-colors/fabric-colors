import subprocess
from pprint import pprint

from fabric.api import env, task
from fabric.colors import green, cyan, red

from fabric_colors.deploy import _env_set
from fabric_colors.utilities.django import (collectstatic, create_public, compilemessages, makemessages)
from fabric_colors.utilities.backups import (postgres_backup, media_backup)
from fabric_colors.environment import set_target_env


PROJECT_NAME = env.project_name
PROJECT_SITES = env.project_sites


@task
@set_target_env
def info():
    """
    Usage: `fab -R dev info`. Show env details of target host "dev".
    """
    try:
        print(green("Our PROJECT_NAME is ") + cyan("{0}".format(PROJECT_NAME)))
        print(green("This is the env variables for host ") + cyan("{0}".format(env.host)))
        pprint(env)
    except:
        print(red("You have not configured your fabsettings properly."))


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
