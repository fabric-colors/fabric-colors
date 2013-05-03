import datetime
import os
from fabric.api import env, get, run, task, sudo
from fabric.contrib.project import rsync_project
from fabric.colors import green, cyan, red

from fabric_colors.deploy import _env_set
from fabric_colors.environment import set_target_env
from fabric.context_managers import prefix
from fabric.contrib import django
from fabric.contrib.files import exists
import pprint



@task
@set_target_env
def mysql_db(local_path='/backups/db/'):
    """
    usage: `fab -R <server_name> backups.mysql_db /path/to/backup/folder/` backups the target's database to local
    Backup path defaults to /backups/db/.
    """

    with prefix(env.activate):
        if env.target != "localhost":
            mod = __import__('{0}.settings'.format(env.project_name),\
                    fromlist=['{0}'.format(env.target)])
            settings = getattr(mod, '{0}'.format(env.target))
        else:
            settings = getattr(mod, 'local')

    timestamp = datetime.datetime.now().strftime("%y-%m-%d_%h-%m-%s")
    fname = '%(dump_path)s%(database)s-backup-%(date)s.sql' % {
        'dump_path': local_path,
        'database': settings.DATABASES['default']['NAME'],
        'date': timestamp,
    }

    # check if local has directory
    if not os.path.exists(local_path):
        print(green("Making local directory"))
        os.makedirs(local_path)

    # check if remote has directory
    if not exists(local_path):
        print(green("Making remote directory"))
        sudo('mkdir -p %s' % local_path)

    print(green("Dumping Database"))
    sudo('mysqldump --user %(username)s --databases %(database)s -p > %(fname)s'
        % {'username': settings.DATABASES['default']['USER'],
           'password': settings.DATABASES['default']['PASSWORD'],
           'database': settings.DATABASES['default']['NAME'],
           'fname': fname})

    print(green("Transferring..."))
    run('rsync -avh %s@%s:%s %s' % (env.user, env.roledefs['demo'][0], fname, fname))

    print(green("Removing remote dump file..."))
    run("rm %(dump_file)s" % {'dump_file': fname})

    print(green("Finish"))

def postgres_backup(target, local_path=None):
    """
    Usage: `fab postgres_backup:dev` `fab postgres_backup:dev,/path/to/backup/folder/`. Backups the target's database to local. Backup path defaults to [cwd]/backups/db/[target]/.
    """
    _env_set(target)

    target_name = target
    if target == 'localhost':
        target_name = 'local'
    # dynamic import for the right target's settings
    import_string = "from {0}.settings.{1} import *".\
            format(env.project_name, target_name)
    exec import_string

    print("Dumping the postgres database")

    dump_path = "/tmp/db_backup"

    run("[ -d %(dump_path)s ] || mkdir %(dump_path)s" % {'dump_path': dump_path})

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    dump_file = "%(path)s/pg_dump_%(target)s_%(timestamp)s.db" % {
        'path': dump_path,
        'target': target,
        'timestamp': timestamp,}
    dump_file_gz = "%(dump_file)s.gz" % {'dump_file': dump_file}

    cmd = [
        "pg_dump",
        "-F c",
    ]
    db_user = DATABASES.get('default', {}).get('USER', '')
    if db_user:
        cmd.append("-U")
        cmd.append(db_user)

    # TODO: add args for host and port

    cmd.append("-f")
    cmd.append(dump_file)

    db_name = DATABASES.get('default', {}).get('NAME', '')
    if db_name:
        cmd.append(db_name)

    result = run(" ".join(cmd))

    result = run("gzip -9q %(dump_file)s" % {'dump_file': dump_file})

    if local_path is None:
        local_path = "%(cwd)s/backups/db/%(target)s" % {'cwd': os.getcwd(), 'target': target}

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    print("Transfering db dump")
    get(dump_file_gz, local_path)

    print("Removing remote dump file")
    run("rm %(dump_file_gz)s" % {'dump_file_gz': dump_file_gz})


def media_backup(target="localhost", local_path=None):
    """
    Usage: `fab media_backup:dev` `fab media_backup:dev,/path/to/backup/folder/`. Backups the target's static files to local. Backup path defaults to [cwd]/backups/static/[target]/.
    """
    _env_set(target)

    target_name = target
    if target == 'localhost':
        target_name = 'local'
    # dynamic import for the right target's settings
    import_string = "from {0}.settings.{1} import *".\
            format(env.project_name, target_name)
    exec import_string

    gz_path = "/tmp/static_backup"

    run("[ -d %(gz_path)s ] || mkdir %(gz_path)s" % {'gz_path': gz_path})

    timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    gz_file = "%(path)s/static_%(target)s_%(timestamp)s.tar.gz" % {
        'path': gz_path,
        'target': target,
        'timestamp': timestamp}

    static_path = env.project_sites.get(target, {}).get('STATIC_PATH', None)
    if static_path == None:
        # TODO: document the requirement of STATIC_PATH in fabsettings
        raise Exception("You must define STATIC_PATH in fabsettings.py for this environment.")

    cmd = ["tar", "cvzpf", gz_file, static_path]
    result = run(" ".join(cmd))

    if local_path is None:
        local_path = "%(cwd)s/backups/static/%(target)s" % {'cwd': os.getcwd(), 'target': target}

    if not os.path.exists(local_path):
        os.makedirs(local_path)

    print("Transfering static files")
    get(gz_file, local_path)

    print("Removing remote tar.gz file")
    run("rm %(gz_file)s" % {'gz_file': gz_file})
