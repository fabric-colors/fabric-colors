from fabric.api import task, env

from fabric_colors.environment import set_target_env


@task
@set_target_env
def webserver(command='restart', newrelic=False):
    """
    command=start/stop/restart/restart_violent; defaults to graceful 'restart' newrelic(optional)=True/False. Wrapper function that restarts the webserver that is current in-use. Defaults to uwsgi.
    """
    print("Command {0} issued to {1}".format(command, env.webserver_type))
    mod = __import__('fabric_colors.webserver.{0}'.format(env.webserver_type), fromlist=['{0}'.format(env.webserver_type)])
    ws = getattr(mod, '{0}'.format(env.webserver_type))
    ws(command, newrelic)


@task
@set_target_env
def initializer():
    """
    Wrapper initializer
    """
    mod = __import__('fabric_colors.webserver.{0}'.format(env.webserver_type), fromlist=['{0}'.format(env.webserver_type)])
    init = getattr(mod, '{0}'.format("initializer"))
    init()
