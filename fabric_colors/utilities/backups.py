import datetime, os
from fabric.api import env, get, run
from fabric_colors.deployment import _env_get

def postgres_backup(target, local_path=None):
    """
    Usage: `fab postgres_backup:dev` `fab postgres_backup:dev,/path/to/backup/folder/`. Backups the target's database to local. Backup path defaults to [cwd]/backups/db/[target]/.
    """
    _env_get(target)
    
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
