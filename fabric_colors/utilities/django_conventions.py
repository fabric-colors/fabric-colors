import os

from fabric.api import env, run
from fabric.context_managers import prefix, cd

from fabric_colors.environment import _env_get


def django_create_public():
    """
    Usage: `fab django_create_public`. Create public directory for django media and static files in our localhost.
    """
    _env_get(target="localhost")
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


def django_collectstatic(target, deploy=False):
    """
    Usage: `fab django_collectstatic:dev`. Run `python manage.py collectstatic` on specified target.
    """
    _env_get(target)
    with prefix(env.activate):
        if deploy:
            working_directory = '%(path)s/releases/%(release)s' % env
        else:
            working_directory = env.path_release_current
        with cd(working_directory):
            #TODO: disable hardcoded target names. Dynamically looking for the correct settings file.
            if target == "dev" or target == "prod":
                run("python manage.py collectstatic --noinput --settings=%s.settings.%s" % (env.project_name, target))
            else:
                run("python manage.py collectstatic --noinput")


def django_makemessages(target, language):
    """
    Usage: `fab django_makemessages:dev,de`. Run `python manage.py makemessages` on specified target and
    language
    """
    _env_get(target)
    with prefix(env.activate):
        with cd(env.path_release_current):
            if target == "dev" or target == "prod":
                run("python manage.py makemessages -l %s --settings=%s.settings.%s" % (language, env.project_name, target))
            else:
                run("python manage.py makemessages -l %s" % language)


def django_compilemessages(target):
    """
    Usage: `fab django_compilemessages:dev`. Run `python manage.py compilemessages` on specified target.
    """
    _env_get(target)
    with prefix(env.activate):
        with cd(env.path_release_current):
            if target == "dev" or target == "prod":
                run("python manage.py compilemessages --settings=%s.settings.%s" % (env.project_name, target))
            else:
                run("python manage.py compilemessages")



