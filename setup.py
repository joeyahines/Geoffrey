from distutils.core import setup

setup(
    name='Geoffrey',
    version=__import__('geoffrey').__version__,
    packages=['geoffrey'],
    install_requires=['discord.py', 'SQLAlchemy', 'pymysql'],
    long_description=open('README.txt').read(),
)
