import time

from fabric.api import run, env
from fabric.context_managers import prefix, cd, settings as fabconfig

from fabric_colors.deployment import _env_get


def _uwsgi_status(target):
    print("Checking the status of our uswgi processes")
    result = run(";if ps aux | grep -v grep | grep -i 'uwsgi'; then echo 'OK'; else echo 'NO'; fi")
    if result.stdout != "NO":
        print("uwsgi is running!")
        return True
    else:
        print("uwsgi is dead!")
        return False


def _uwsgi_start(target, env, newrelic):
    if newrelic:
        print("Starting uwsgi with NEW_RELIC_CONFIG_FILE")
        run("NEW_RELIC_CONFIG_FILE=%s/newrelic.ini \
                newrelic-admin run-program uwsgi --ini %s/uwsgi_%s.ini"
                % (env.path_release_current, env.project_path, target))
    else:
        print("Starting uwsgi")
        run("uwsgi --ini %s/uwsgi_%s.ini" % (env.project_path, target))


def _uwsgi_restart(target, env, newrelic):
    if _uwsgi_status(target):
        print("Restarting uwsgi processes gracefully")
        run("kill -HUP `cat /tmp/%s.pid-3030`" % env.project_name)
    else:
        print("uwsgi processes are already dead. executing a start.")
        _uwsgi_start(target, env, newrelic)


def _uwsgi_restart_violent(target, env, newrelic):
    print("Restarting uwsgi processes violently")
    run("kill -INT `cat /tmp/%s.pid-3030`" % env.project_name)
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
                run("uwsgi --stop /tmp/%s.pid-3030" % env.project_name)
            elif command == "restart":
                _uwsgi_restart(target, env, newrelic)
            elif command == "restart_violent":
                _uwsgi_restart_violent(target, env, newrelic)
            elif command == "status":
                _uwsgi_status(target)
