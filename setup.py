from setuptools import setup

setup(
    name='Fabric Colors',
    version='0.8.4',
    packages=['fabric_colors', ],
    license='LICENSE',
    description='Reusable fabric functions',
    long_description=open('README.md').read(),
    author='Calvin Cheng',
    author_email='calvin@calvinx.com',
    install_requires=['distribute', 'Fabric>=1.4.3'],
    test_require=[],
    test_suite='tests',
    entry_points={
        'console_scripts': [
            'fabc = fabric_colors.main:main',
        ]
    }
)
