import discord
import enum
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker

TOKEN = ''
command_prefix = '?'
description = '''
Geoffrey started his life as inside joke none of you will understand.
At some point, she was to become an airhorn bot. Now, they know where your bases are.

Please respect Geoffrey, the bot is very sensitive.
'''

engine = create_engine('sqlite:///:memory:', echo=True)
SQL_Base = declarative_base()

bot = commands.Bot(command_prefix=command_prefix, description=description, case_insensitive=True)


class DataBaseError(Exception):
    '''Base class for exceptions in this module.'''
    pass


class LocationInitError(DataBaseError):
    '''Error in initializing Location'''


class LocationLookUpError(DataBaseError) :
    '''Error in finding location in database'''


class TunnelDirection(enum.Enum):
    North = 'green'
    East = 'blue'
    South = 'red'
    West = 'yellow'


class Player(SQL_Base):
    __tablename__ = 'Players'

    id = Column(Integer, primary_key=True)
    in_game_name = Column(String)

    def __init__(self, name):
        self.in_game_name = name


class Location(SQL_Base):
    __tablename__ = 'Locations'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    x = Column(Integer)
    y = Column(Integer)
    z = Column(Integer)
    tunnelNumber = Column(Integer)
    direction = Column(Enum(TunnelDirection))
    owner = Column(String, ForeignKey('Players.in_game_name'))

    def __init__(self, args, owner):
        try:
            self.name = args[0]
            self.x = int(args[1])
            self.y = int(args[2])
            self.z = int(args[3])
            self.owner = owner

            if len(args) >= 5:
                self.tunnelNumber = int(args[5])
                self.direction = strToTunnelDirection(args[4])
        except (ValueError, IndexError):
            raise LocationInitError

    def pos_to_str(self):
        return '(x= {}, y= {}, z= {})'.format(self.x, self.y, self.z)

    def nether_tunnel_addr_to_str(self):
        return '{} {}'.format(self.direction.value.title(), self.tunnelNumber)

    def __str__(self):
        if self.direction is not None:
            return "Name: {}, Position: {}, Tunnel: {}".format(self.name, self.pos_to_str(), self.nether_tunnel_addr_to_str())
        else:
            return "Name: {}, Position: {}".format(self.name, self.pos_to_str())


SQL_Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()


def strToTunnelDirection(arg):
    arg = arg.lower()
    if (arg == TunnelDirection.North.value):
        return TunnelDirection.North
    elif (arg == TunnelDirection.East.value):
        return TunnelDirection.East
    elif (arg == TunnelDirection.South.value):
        return TunnelDirection.South
    elif (arg == TunnelDirection.West.value):
        return TunnelDirection.West
    else:
        raise ValueError


# Bot Commands ******************************************************************


@bot.event
async def on_ready():
    print('GeoffreyBot')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        error_str = 'Command not found, please use ?help to see all the commands this bot can do.'
    elif isinstance(error, commands.UserInputError):
        error_str = 'Invalid syntax for {}, please read ?help {}.'.format(ctx.invoked_with, ctx.invoked_with)
    else:
        error_str = 'Error using the {} command, yell at the admins to fix it'.format(ctx.invoked_with)

    await bot.send_message(ctx.message.channel, error_str)


@bot.command()
async def test():
    '''Check if the bot is alive.'''
    await bot.say('I\'m here you ding dong')


@bot.command(pass_context=True)
async def addbase(ctx, *args, ):
    '''
    Add your base to the database.
     The tunnel address is optional.
     ?addbase [Base Name] [X Coordinate] [Y Coordinate] [Z Coordinate] [Tunnel Color] [Tunnel Position]
    '''

    owner = Player(str(ctx.message.author.nick))
    base = Location(args, owner.in_game_name)

    session.add(owner)
    session.add(base)

    await bot.say('{}, your base named {} located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))


@bot.command(pass_context=True)
async def findbase(ctx, *args):
    '''Allows you to find a base in the database.
        ?findbase [Player name]
    '''
    search_key = args[0]
    baseList = session.query(Location).filter_by(owner=search_key).all()

    if baseList is not None:
        await bot.say('{}, {} has {} base(s):'.format(ctx.message.author.mention, args[0], len(baseList)))
        for base in baseList:
            await bot.say(base)
    else:
        await bot.say('{}, {} is not in the database'.format(ctx.message.author.mention, args[0]))

# Bot Startup ******************************************************************

try:
    file = open('token.dat', 'r')
    TOKEN = file.read()
except FileNotFoundError:
    print('token.dat not found.')
except IOError:
    print('Error reading token.dat')

bot.run(TOKEN)
