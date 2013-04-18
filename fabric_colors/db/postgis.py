from fabric.api import task, run, sudo

from fabric_colors.environment import set_target_env


@task
@set_target_env
def install():
    """
    Install postgis if it is not yet installed.
    """
    if not installed():
        sudo('pacman -S postgis --noconfirm')


@task
@set_target_env
def installed():
    """
    Check if postgis is installed.
    """
    pkg = "pacman -Qs postgis"
    cmd = """
        pkg=`{0}`
        if [ -n "$pkg" ]; then echo 1; else echo ""; fi""".format(pkg)
    return run(cmd)


@task
@set_target_env
def create_template():
    command_string = """
        POSTGIS_SQL_PATH=`pg_config --sharedir`/contrib/postgis-2.0
        # Creating the template spatial database.
        createdb -U postgres -E UTF8 template_postgis
        createlang -U postgres -d template_postgis plpgsql # Adding PLPGSQL language support.
        # Allows non-superusers the ability to create from this template
        psql -U postgres -d postgres -c "UPDATE pg_database SET datistemplate='true' WHERE datname='template_postgis';"
        # Loaing the PostGIS SQL routines
        psql -U postgres -d template_postgis -f $POSTGIS_SQL_PATH/postgis.sql
        psql -U postgres -d template_postgis -f $POSTGIS_SQL_PATH/spatial_ref_sys.sql
        # Enabling users to alter spatial tables.
        psql -U postgres -d template_postgis -c "GRANT ALL ON geometry_columns TO PUBLIC;"
        psql -U postgres -d template_postgis -c "GRANT ALL ON geography_columns TO PUBLIC;"
        psql -U postgres -d template_postgis -c "GRANT ALL ON spatial_ref_sys TO PUBLIC;"
    """
    run(command_string)
