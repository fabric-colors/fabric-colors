import time

from fabric.api import run, env
from fabric.context_managers import prefix, cd, settings as fabconfig

from fabric_colors.deployment import _env_get

import fabsettings


def _uwsgi_chk_log(target):
    print("Checking if we have a log directory and file for our uwsgi process")
    cmd = "[ -d {0}/{1}_uwsgi ] && echo '1'".format(env.path_releases, env.project_name)
    result = run(cmd)
    return result


def _uwsgi_mk_log(target):
    cmd = "mkdir -p {0}/{1}_uwsgi".format(env.path_releases, env.project_name)
    cmd2 = "touch {0}/{1}_uwsgi/{2}.log".format(env.path_releases, env.project_name, env.project_name)
    run(cmd)
    run(cmd2)


def _uwsgi_status(target):
    print("Checking the status of our uswgi processes")
    result = run(";if ps aux | grep -v grep | grep -i 'uwsgi'; then echo 'OK'; else echo 'NO'; fi")
    if result.stdout != "NO":
        print("uwsgi is running!")
        return True
    else:
        print("uwsgi is dead!")
        return False


def _uwsgi_start(target, env, newrelic=False):

    if newrelic:
        # If user provides a value here, we will restart uwsgi with the newrelic
        # command
        newrelic = True
    else:
        # Otherwise, we will check for its presence in fabsettings, failing
        # which we will finally default to False
        newrelic = fabsettings.PROJECT_SITES[target].get('NEW_RELIC', False)

    if newrelic:
        print("Starting uwsgi with NEW_RELIC_CONFIG_FILE")
        run("NEW_RELIC_CONFIG_FILE=%s/newrelic.ini \
                newrelic-admin run-program uwsgi --ini {0}/uwsgi_{1}.ini".format(env.path_release_current, env.project_path, target))
    else:
        print("Starting uwsgi")
        result = _uwsgi_chk_log(target)
        if not result:
            _uwsgi_mk_log(target)
        run("uwsgi --ini {0}/uwsgi_{1}.ini".format(env.project_path, target))


def _uwsgi_restart(target, env, newrelic):
    if _uwsgi_status(target):
        print("Restarting uwsgi processes gracefully")
        run("kill -HUP `cat /tmp/{0}.pid-{1}`".format(env.project_name, env.webserver_port))
    else:
        print("uwsgi processes are already dead. executing a start.")
        _uwsgi_start(target, env, newrelic)


def _uwsgi_restart_violent(target, env, newrelic):
    print("Restarting uwsgi processes violently")
    run("kill -INT `cat /tmp/{0}.pid-{1}`".format(env.project_name, env.webserver_port))
    time.sleep(1)
    _uwsgi_start(target, env, newrelic)


def uwsgi(target, command, newrelic=False):
    """
    e.g. `fab uwsgi:dev,restart`  possible options - start/stop/restart/restart_violent/status \
    and optional 3rd argument if present, will invoke newrelic call, assuming server has newrelic installed
    """
    _env_get(target)
    with prefix(env.activate):
        with cd(env.path_release_current) and fabconfig(warn_only=True):
            if command == "start":
                print("Starting uwsgi processes")
                _uwsgi_start(target, env, newrelic)
            elif command == "stop":
                print("Stopping uwsgi processes")
                run("uwsgi --stop /tmp/{0}.pid-{1}".format(env.project_name, env.webserver_port))
            elif command == "restart":
                _uwsgi_restart(target, env, newrelic)
            elif command == "restart_violent":
                _uwsgi_restart_violent(target, env, newrelic)
            elif command == "status":
                _uwsgi_status(target)
