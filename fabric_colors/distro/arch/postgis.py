PKG_INSTALL = 'sudo pacman -S postgis --noconfirm'
PKG_INSTALLED = 'pacman -Qs postgis'
PKG_INSTALLED_CMD = """
    pkg=`{0}`
    if [ -n "$pkg" ]; then echo 1; else echo ""; fi
    """.format(PKG_INSTALLED)
