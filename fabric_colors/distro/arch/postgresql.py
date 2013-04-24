PKG_INSTALL = 'sudo pacman -S postgresql --noconfirm'
PKG_CLIENT_INSTALL = None
PKG_INSTALLED = 'pacman -Qs postgresql'
PKG_CLIENT_INSTALLED = None

PKG_INSTALLED_CMD = """
    pkg=`{0}`
    if [ -n "$pkg" ]; then echo 1; else echo 0; fi
""".format(PKG_INSTALLED)

PKG_CLIENT_INSTALLED_CMD = None

DEFAULT_DATA_DIR = "/var/lib/postgres/data"
INITIALIZE_DB = """su - postgres -c 'initdb --locale en_US.UTF-8 -D "{0}"'""".format(DEFAULT_DATA_DIR)
INITIALIZER = "sudo systemctl enable postgresql"
START = "sudo systemctl start postgresql"
STOP = "sudo systemctl stop postgresql"
RESTART = "sudo systemctl restart postgresql"
