from setuptools import setup

# Computer version number from _version.py
import re
VERSIONFILE = "fabric_colors/_version.py"
verstrline = open(VERSIONFILE, "rt").read()
VSRE = r"^__version__ = ['\"]([^'\"]*)['\"]"
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % (VERSIONFILE,))

setup(
    name='Fabric Colors',
    version=verstr,
    packages=['fabric_colors', ],
    license='LICENSE',
    description='Reusable fabric functions',
    long_description=open('README.md').read(),
    author='Calvin Cheng',
    author_email='calvin@calvinx.com',
    install_requires=['distribute', 'colorama', 'configobj', 'Fabric>=1.6.0'],
    tests_require=[],
    test_suite='fabric_colors.tests',
    entry_points={
        'console_scripts': [
            'fabc = fabric_colors.main:main',
            'fabc-quickstart = fabric_colors.quickstart:quickstart',
        ]
    }
)
