PKG_INSTALL = 'sudo port -v install postgis2'
PKG_INSTALLED = 'port installed postgis2'
PKG_INSTALLED_CMD = """
        pkg=$(port installed postgis2)
        if [[ $pkg = *"None of the specified ports are installed"* ]];
        then echo "";
        else echo 1;
        fi""".format(PKG_INSTALLED)
