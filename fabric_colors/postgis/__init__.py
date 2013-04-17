from fabric.api import run, local

from fabric_colors.deploy import _env_set


def create_postgis_template(target):
    _env_set(target)
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
    if target == "localhost":
        local(command_string)
    else:
        run(command_string)
