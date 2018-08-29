from distutils.core import setup

setup(
    name='Geoffrey',
    version=__import__('geoffrey').__version__,
    packages=['geoffrey', 'geoffrey.cogs'],
    install_requires=['discord.py', 'SQLAlchemy', 'pymysql', 'requests'],
    long_description=open('README.txt').read(),
)
