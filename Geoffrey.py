from discord.ext import commands
from DatabaseModels import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *

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


# Bot Commands ******************************************************************'


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
    elif isinstance(error.original, UsernameLookupFailed):
        error_str = error.original.__doc__
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

    player_name = get_nickname(ctx.message.author)

    try:
        base = database.add_base(player_name, name, x_pos, y_pos, z_pos, args)
    except LocationInitError:
        raise commands.UserInputError

    await bot.say('{}, your base named {} located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))

@bot.command(pass_context=True)
async def addshop(ctx, name: str, x_pos: int, y_pos: int, z_pos: int, * args):
    '''
    Adds a shop to the database.
     The tunnel address is optional.
     ?addbase [Shop name] [X Coordinate] [Y Coordinate] [Z Coordinate] [Tunnel Color] [Tunnel Position]
    '''

    player_name = get_nickname(ctx.message.author)

    try:
        base = database.add_shop(player_name, name, x_pos, y_pos, z_pos, args)
    except LocationInitError:
        raise commands.UserInputError

    await bot.say('{}, your shop named {} located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))


@bot.command(pass_context=True)
async def find(ctx, name: str):
    '''
    Finds all the locations a player has in the database.
        ?find [Player name]
    '''

    base_list = database.find_location_by_owner(name)

    if len(base_list) != 0:
        base_string = loc_list_to_string(base_list, '{} \n{}')

        await bot.say('{}, {} has {} base(s): \n {}'.format(ctx.message.author.mention, name, len(base_list),
                                                            base_string))
    else:
        await bot.say('{}, the player {} is not in the database'.format(ctx.message.author.mention, name))


@bot.command(pass_context=True)
async def delete(ctx, name: str):
    '''
    Deletes a location from the database.
        ?delete [Location name]
    '''

    player_name = get_nickname(ctx.message.author)
    try:
        database.delete_base(player_name, name)
        await bot.say('{}, your base named "{}" has been deleted.'.format(ctx.message.author.mention, name))
    except DeleteEntryError:
        await bot.say('{}, you do not have a base named "{}".'.format(ctx.message.author.mention, name))


@bot.command(pass_context=True)
async def findaround(ctx, x_pos: int, z_pos: int, * args):
    '''
    Finds all the bases/shops around a certain point that are registered in the database
    The Radius argument defaults to 200 blocks if no value is given
        ?findbasearound [X Coordinate] [Z Coordinate] [Radius]
    '''

    radius = 200
    if len(args) > 0:
        try:
            radius = int(args[0])
        except ValueError:
            raise commands.UserInputError

    base_list = database.find_location_around(x_pos, z_pos, radius)

    if len(base_list) != 0:
        base_string = loc_list_to_string(base_list, '{} \n{}')

        await bot.say('{}, there are {} base(s) within {} blocks of that point: \n {}'.format(
            ctx.message.author.mention, len(base_list), radius, base_string))
    else:
        await bot.say('{}, there are no bases within {} blocks of that point'
                      .format(ctx.message.author.mention, radius))


@bot.command(pass_context=True)
async def additem(ctx, shop_name: str, item_name: str, diamond_price: int):
    '''
    Adds an item to a shop's inventory
        ?additem [Shop name] [Item Name] [Price]
    '''
    player_name = get_nickname(ctx.message.author)
    database.add_item(player_name, shop_name, item_name, diamond_price)

    await bot.say('{}, {} has been added to the inventory of {}.'.format(ctx.message.author.mention,
                                                                         item_name, shop_name))


@bot.command(pass_context=True)
async def selling(ctx, item_name: str):
    '''
    Lists all the shops selling an item
        ?selling [item]
    '''
    shop_list = database.find_shop_selling_item(item_name)

    shop_list_str = loc_list_to_string(shop_list)
    await bot.say('The following shops sell {}: \n {}'.format(item_name, shop_list_str))


# Helper Functions ************************************************************


def get_nickname(discord_user) :
    if discord_user.nick is None:
        return discord_user.display_name
    else:
        return discord_user.nick


def loc_list_to_string(loc_list, str_format='{}\n{}'):
    loc_string = ''

    for loc in loc_list:
        loc_string = str_format.format(loc_string, loc)

    return loc_string

# Bot Startup ******************************************************************


try:
    file = open('token.dat', 'r')
    TOKEN = file.read()
except FileNotFoundError:
    print('token.dat not found.')
except IOError:
    print('Error reading token.dat')

bot.run(TOKEN)
