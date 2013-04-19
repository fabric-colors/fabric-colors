import time
import mmap
import os
import re

from fabric.api import run, env, task, local
from fabric.colors import green
from fabric.context_managers import prefix, cd, settings as fabconfig
from fabric.operations import put

from fabric_colors.environment import set_target_env


@set_target_env
def _uwsgi_chk_log():
    print("Checking if we have a log directory and file for our uwsgi process")
    cmd = "[ -d {0}/{1}_uwsgi ] && echo '1'".format(env.path_releases, env.project_name)
    result = run(cmd)
    return result


@set_target_env
def _uwsgi_mk_log():
    cmd = "mkdir -p {0}/{1}_uwsgi".format(env.path_releases, env.project_name)
    cmd2 = "touch {0}/{1}_uwsgi/{2}.log".format(env.path_releases, env.project_name, env.project_name)
    run(cmd)
    run(cmd2)


@set_target_env
def _uwsgi_status():
    print("Checking the status of our uswgi processes")
    result = run("if ps aux | grep -v grep | grep -i 'uwsgi'; then echo 'OK'; else echo 'NO'; fi")
    if result.stdout != "NO":
        print("uwsgi is running!")
        return True
    else:
        print("uwsgi is dead!")
        return False


@set_target_env
def _uwsgi_start(newrelic=False):

    if newrelic:
        # If user provides a value here, we will restart uwsgi with the newrelic
        # command
        newrelic = True
    else:
        # Otherwise, we will check for its presence in fabsettings, failing
        # which we will finally default to False
        newrelic = env.newrelic

    result = _uwsgi_chk_log()
    if not result:
        _uwsgi_mk_log()

    if newrelic:
        print(green("Starting uwsgi with NEW_RELIC_CONFIG_FILE"))
        run("NEW_RELIC_CONFIG_FILE={0}/newrelic.ini \
                newrelic-admin run-program uwsgi --ini {1}/uwsgi_{2}.ini".format(env.path_release_current, env.project_path, env.target))
    else:
        print("Starting uwsgi")
        run("uwsgi --ini {0}/uwsgi_{1}.ini".format(env.project_path, env.target))


@set_target_env
def _uwsgi_restart(newrelic):
    if _uwsgi_status():
        print("Restarting uwsgi processes gracefully")
        run("kill -HUP `cat /tmp/{0}.pid-{1}`".format(env.project_name, env.webserver_port))
    else:
        print("uwsgi processes are already dead. executing a start.")
        _uwsgi_start(newrelic)


@set_target_env
def _uwsgi_restart_violent(newrelic):
    print("Restarting uwsgi processes violently")
    run("kill -INT `cat /tmp/{0}.pid-{1}`".format(env.project_name, env.webserver_port))
    time.sleep(1)
    _uwsgi_start(newrelic)


@task(default=True)
@set_target_env
def uwsgi(command, newrelic=False):
    """
    Usage: `fab -R all uwsgi:command`. command=start/stop/restart/restart_violent/status, newrelic(optional)=True/False.
    """
    with prefix(env.activate):
        with cd(env.path_release_current) and fabconfig(warn_only=True):
            if command == "start":
                print("Starting uwsgi processes")
                _uwsgi_start(newrelic)
            elif command == "stop":
                print("Stopping uwsgi processes")
                run("uwsgi --stop /tmp/{0}.pid-{1}".format(env.project_name, env.webserver_port))
            elif command == "restart":
                _uwsgi_restart(newrelic)
            elif command == "restart_violent":
                _uwsgi_restart_violent(newrelic)
            elif command == "status":
                _uwsgi_status()


@task
@set_target_env
def initializer():
    """
    Check if host has the current project's uwsgi initializer. If not, create it.
    """
    path_to_initializer = "/usr/lib/systemd/system/"
    initializer_name = env.project_name + "_" + env.target + ".service"
    path = path_to_initializer + initializer_name
    print("Checking if {0} is available".format(initializer_name))
    cmd = """if [ -e "{0}" ]; then echo 1; else echo ""; fi""".format(path)
    results = run(cmd)
    if results:
        print("{0} is already available in the host.".format(initializer_name))
        exit()

    template_file = os.path.dirname(__file__) + "/uwsgi.service.template"
    f = open(template_file)
    s = mmap.mmap(f.fileno(), 0, access=mmap.ACCESS_READ)
    matches = re.findall(r'{[^{}]*}', s)
    unique_matches = (list(set(matches)))
    text = s[:]
    dic = {}
    for um in unique_matches:
        replacement_string = env.get(um[1:][:-1])
        #print("{0} to be replaced by {1}".format(um, replacement_string))
        dic[um] = replacement_string

    text = replace_all(text, dic)
    s.close()
    f.close()
    new_file = '{0}_{1}.service'.format(env.project_name, env.target)
    f_new = open(new_file, 'w+')
    f_new.write(text)
    f_new.close()
    put(new_file, path_to_initializer, use_sudo=True)
    sudo("systemctl enable {0}".format(new_file))
    local('rm {0}'.format(new_file))


def replace_all(text, dic):
    for i, j in dic.iteritems():
        text = text.replace(i, j)
    return text
