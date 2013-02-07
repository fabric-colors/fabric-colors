__all__ = ['deploy', 'mkvirtualenv']

import os
import sys
import subprocess

from fabric.api import env, run, sudo, require
from fabric.context_managers import prefix, cd, hide, settings as fabconfig
from fabric_colors.environment import _env_get
from fabric_colors.deployment.git import git_branch_check, git_archive_and_upload_tar
from fabric_colors.utilities.django_conventions import django_collectstatic, django_compilemessages


def deploy(target, email=False):
    """
    Usage: `fab deploy:dev`. Execute a deployment to the given target machine.
    """
    _env_get(target)
    env.release = str(subprocess.Popen(["git", "rev-parse", "--short", "HEAD"], \
            stdout=subprocess.PIPE).communicate()[0]).rstrip()
    if git_branch_check():
        git_archive_and_upload_tar()
        pip_install_requirements()
        symlink_current_release()
        django_collectstatic(target)
        try:
            django_compilemessages(target)
        except:
            pass
        if email:
            # dynamic import for the right target's settings
            import_string = "from {0}.settings.{1} import *".\
                    format(env.project_name, target)
            exec import_string

            # Execute email
            from django.core.mail import EmailMessage, BadHeaderError
            from django.core import mail
            print dir(mail)
            subject = 'Deployed to {0}'.format(target)
            message = 'Deployed to {0}'.format(target)
            from_address = DEFAULT_FROM_EMAIL
            admin_emails = [a[1] for a in ADMINS]
            em = EmailMessage(subject, message, from_address, admin_emails)

            try:
                mail_connection = mail.get_connection()
                mail_connection.send_messages([em])
                print("Deployment notification sent to {0}".format(str(admin_emails)[1:-1]))
            except BadHeaderError, e:
                print e
                print("Invalid header found.")


def mkvirtualenv(target):
    """
    Create the virtualenv for our project on the target machine. `fab mkvirtualenv:dev`
    """
    _env_get(target)
    run('mkvirtualenv -p python2.7 --distribute %s' % (env.project_name))


def prepare_deploy_env(target):
    """
    Make sure that we have the release directories before executing deployment.
    """
    _env_get(target)
    result = run('; if [ -d "{0}" ]; then echo 1; else echo ""; fi'.format(env.path_releases))
    print result.stdout
    if not result.stdout:
        sudo('; mkdir -p {0}'.format(env.path_releases))
        sudo('; chown {0}:{0} -R {1}'.format(env.user, env.path))
    else:
        print("{0} already exists".format(env.path_releases))


def pip_install_requirements():
    """
    Install the required python packages from the requirements.txt file using pip
    """
    require('release', provided_by=[deploy])
    with prefix(env.activate):
        run('&& pip install -r %(path)s/releases/%(release)s/requirements.txt' % env)


def symlink_current_release():
    """
    Symlink our current release
    """
    require('release', provided_by=[deploy])
    with cd(env.path):
        if symlink_check():
            run('cd releases; rm current; ln -s %(release)s current' % env)
        else:
            run('cd releases; ln -s %(release)s current' % env)


def symlink_check():
    """
    Check the hash pointing to the current symlink
    """
    with cd(env.path):
        cmd = "cd releases; [ -d current ] && echo '1'"
        with fabconfig(hide('everything'), warn_only=True):
            return bool(run(cmd))
