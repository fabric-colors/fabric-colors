import os

from fabric.api import env, run, task
from fabric.context_managers import prefix, cd
from fabric_colors.environment import _env_set, set_target_env


@task
@set_target_env
def create_public():
    """
    Usage: `fab -R dev django.create_public`. Create public directory for django media and static files in our localhost.
    """
    _env_set(target="localhost")
    public_dir = os.path.join(env.project_path,
            env.project_name + "_public")

    if not os.path.exists(public_dir):
        os.makedirs(public_dir)
        print public_dir + " has been created."
    else:
        print public_dir + " already exists."

    try:
        f = open(public_dir + "/index.html", "w")
    except IOError:
        pass

    if f:
        f.close()


@task
@set_target_env
def collectstatic(deploy=False):
    """
    Usage: `fab -R dev django.collectstatic`. Run `python manage.py collectstatic` on specified target.
    """
    with prefix(env.activate):
        if deploy:
            working_directory = '%(path)s/releases/%(release)s' % env
        else:
            working_directory = env.path_release_current
        with cd(working_directory):
            if env.target:
                run("python manage.py collectstatic --noinput --settings=%s.settings.%s" % (env.project_name, env.target))
            else:
                run("python manage.py collectstatic --noinput")


@task
@set_target_env
def makemessages(language):
    """
    Usage: `fab -R dev django.makemessages:de`. Run `python manage.py makemessages` on specified target and
    language
    """
    with prefix(env.activate):
        with cd(env.path_release_current):
            if env.target:
                run("python manage.py makemessages -l %s --settings=%s.settings.%s" % (language, env.project_name, env.target))
            else:
                run("python manage.py makemessages -l %s" % language)


@task
@set_target_env
def compilemessages():
    """
    Usage: `fab -R dev django.compilemessages`. Run `python manage.py compilemessages` on specified target.
    """
    with prefix(env.activate):
        with cd(env.path_release_current):
            if env.target:
                run("python manage.py compilemessages --settings=%s.settings.%s" % (env.project_name, env.target))
            else:
                run("python manage.py compilemessages")
