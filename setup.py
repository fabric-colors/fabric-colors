from setuptools import setup

setup(
    name='Fabric Colors',
    version='0.9.14',
    packages=['fabric_colors', ],
    license='LICENSE',
    description='Reusable fabric functions',
    long_description=open('README.md').read(),
    author='Calvin Cheng',
    author_email='calvin@calvinx.com',
    install_requires=['distribute', 'colorama', 'configobj', 'Fabric>=1.4.3'],
    tests_require=[],
    test_suite='fabric_colors.tests',
    entry_points={
        'console_scripts': [
            'fabc = fabric_colors.main:main',
            'fabc-quickstart = fabric_colors.quickstart:quickstart',
        ]
    }
)
