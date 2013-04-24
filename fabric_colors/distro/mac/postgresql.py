PKG_INSTALL = 'sudo port -v install postgresql92-server'
PKG_CLIENT_INSTALL = 'sudo port -v install postgresql92'
PKG_INSTALLED = 'port installed postgresql92-server'
PKG_CLIENT_INSTALLED = 'port installed postgresql92'

PKG_INSTALLED_CMD = """
        pkg=$({0})
        if [[ $pkg = *"None of the specified ports are installed"* ]];
        then echo 0;
        else echo 1;
        fi""".format(PKG_INSTALLED)

PKG_CLIENT_INSTALLED_CMD = """
        pkg=$({0})
        if [[ $pkg = *"None of the specified ports are installed"* ]];
        then echo 0;
        else echo 1;
        fi""".format(PKG_CLIENT_INSTALLED)

DEFAULT_DATA_DIR = "/opt/local/var/db/postgresql92/defaultdb"
INITIALIZE_DB = """
    sudo su postgres -c '/opt/local/lib/postgresql92/bin/initdb --locale en_US.UTF-8 -D {0}
""".format(DEFAULT_DATA_DIR)
INITIALIZER = """
    sudo launchctl load -w /Library/LaunchDaemons/org.macports.postgresql92-server.plist
"""
START = """
    sudo su postgres -c '/opt/local/lib/postgresql92/bin/postgres -D {0}'
""".format(DEFAULT_DATA_DIR)
RESTART = """
    sudo su postgres -c 'pg_ctl -D {0} restart'
""".format(DEFAULT_DATA_DIR)
