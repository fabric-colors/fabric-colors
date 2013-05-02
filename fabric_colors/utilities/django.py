import os

from fabric.api import env, run
from fabric.context_managers import prefix, cd

from fabric_colors.environment import _env_set, set_target_env


@task
@set_target_env
def create_public():
    """
    Usage: `fab django_create_public`. Create public directory for django media and static files in our localhost.
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
    Usage: `fab django_collectstatic:dev`. Run `python manage.py collectstatic` on specified target.
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
def makemessages(target, language):
    """
    Usage: `fab django_makemessages:dev,de`. Run `python manage.py makemessages` on specified target and
    language
    """
    _env_set(target)
    with prefix(env.activate):
        with cd(env.path_release_current):
            if target == "dev" or target == "prod":
                run("python manage.py makemessages -l %s --settings=%s.settings.%s" % (language, env.project_name, target))
            else:
                run("python manage.py makemessages -l %s" % language)


@task
@set_target_env
def compilemessages(target):
    """
    Usage: `fab django_compilemessages:dev`. Run `python manage.py compilemessages` on specified target.
    """
    _env_set(target)
    with prefix(env.activate):
        with cd(env.path_release_current):
            if target == "dev" or target == "prod":
                run("python manage.py compilemessages --settings=%s.settings.%s" % (env.project_name, target))
            else:
                run("python manage.py compilemessages")



