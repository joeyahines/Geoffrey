from discord.ext import commands
from DatabaseModels import *
from BotErrors import *

TOKEN = ''
command_prefix = '?'
description = '''
Geoffrey started his life as inside joke none of you will understand.
At some point, she was to become an airhorn bot. Now, they know where your bases/shops are.

Please respect Geoffrey, the bot is very sensitive.w
'''

bad_error_message = 'OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The admins at our ' \
                        'headquarters are working VEWY HAWD to fix this! (Error in command {})'

bot = commands.Bot(command_prefix=command_prefix, description=description, case_insensitive=True)

database = GeoffreyDatabase('sqlite:///:memory:')

# Bot Commands ******************************************************************
@bot.event
async def on_ready():
    print('GeoffreyBot')
    print('Username: ' + bot.user.name)
    print('ID: ' + bot.user.id)


@bot.event
async def on_command_error(error, ctx):
    if isinstance(error, commands.CommandNotFound):
        error_str = 'Command not found, ding dongs like you can use ?help to see all the commands this bot can do.'
    elif isinstance(error, commands.UserInputError):
        error_str = 'Invalid syntax for {} you ding dong, please read ?help {}.'\
            .format(ctx.invoked_with, ctx.invoked_with)
    else:
        error_str = bad_error_message.format(ctx.invoked_with)
        print(error)

    await bot.send_message(ctx.message.channel, error_str)


@bot.command()
async def test():
    '''
    Checks if the bot is alive.
    '''
    await bot.say('I\'m here you ding dong')


@bot.command(pass_context=True)
async def addbase(ctx, name: str, x_pos: int, y_pos: int, z_pos: int, * args):
    '''
    Add your base to the database.
     The tunnel address is optional.
     ?addbase [Base Name] [X Coordinate] [Y Coordinate] [Z Coordinate] [Tunnel Color] [Tunnel Position]
    '''

    owner = Player(str(ctx.message.author.nick))

    try:
        base = Location(name, x_pos, y_pos, z_pos, owner.in_game_name, args)
    except LocationInitError:
        raise commands.UserInputError

    database.add_object(owner)
    database.add_object(base)

    await bot.say('{}, your base named {} located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))


@bot.command(pass_context=True)
async def findbase(ctx, name: str):
    '''
    Finds a base in the database.
        ?findbase [Player name]
    '''

    expr = Location.owner == name
    base_list = database.query_by_filter(Location, expr)

    if len(base_list) != 0:
        base_string = base_list_string(base_list, '{} \n{}')

        await bot.say('{}, {} has {} base(s): \n {}'.format(ctx.message.author.mention, name, len(base_list),
                                                            base_string))
    else:
        await bot.say('{}, the player {} is not in the database'.format(ctx.message.author.mention, name))


def base_list_string(base_list, str_format):
    base_string = ''

    for base in base_list:
        base_string = str_format.format(base_string, base)

    return base_string


@bot.command(pass_context=True)
async def deletebase(ctx, name: str):
    '''
    Deletes a base from the database.
        ?deletebase [Base name]
    '''

    user = str(ctx.message.author.nick)

    expr = (Location.owner == user) & (Location.name == name)

    try:
        database.delete_entry(Location, expr)
        await bot.say('{}, your base named "{}" has been deleted.'.format(ctx.message.author.mention, name))
    except DeleteEntryError:
        await bot.say('{}, you do not have a base named "{}".'.format(ctx.message.author.mention, name))

@bot.command(pass_context=True)
async def findbasearound(ctx, x_pos: int, z_pos: int, * args):
    '''
        Finds all the base around a certain point that are registered in the database
        The Radius argument defaults to 200 blocks if no value is given
            ?findbasearound [X Coordinate] [Z Coordinate] [Radius]
    '''

    radius = 200
    if len(args) > 0:
        try:
            radius = int(args[0])
        except ValueError:
            raise commands.UserInputError

    expr = (Location.x < x_pos + radius) & (Location.x > x_pos - radius) & (Location.z < z_pos + radius) & \
           (Location.z > z_pos - radius)

    base_list = database.query_by_filter(Location, expr)

    if len(base_list) != 0:
        base_string = base_list_string(base_list, '{} \n{}')

        await bot.say('{}, there are {} base(s) within {} blocks of that point: \n {}'.format(
            ctx.message.author.mention, len(base_list), radius, base_string))
    else:
        await bot.say('{}, there are no bases within {} blocks of that point'
                      .format(ctx.message.author.mention, radius))

# Bot Startup ******************************************************************
try:
    file = open('token.dat', 'r')
    TOKEN = file.read()
except FileNotFoundError:
    print('token.dat not found.')
except IOError:
    print('Error reading token.dat')

bot.run(TOKEN)
