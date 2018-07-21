from discord.ext import commands
from DatabaseModels import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *
from itertools import zip_longest
import configparser
import shlex
#from WebInterface import *

TOKEN = ''
command_prefix = '?'
description = '''
Geoffrey started his life as an inside joke none of you will understand.
At some point, she was to become an airhorn bot. Now, they know where your bases/shops are.

Please respect Geoffrey, the bot is very sensitive.

*You must use ?register before adding entries into Geoffrey*
'''

bad_error_message = 'OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The admins at our ' \
                        'headquarters are working VEWY HAWD to fix this! (Error in command {}: {})'

bot = commands.Bot(command_prefix=command_prefix, description=description, case_insensitive=True)

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
        database_interface.database.session.rollback()
    elif isinstance(error.original, UsernameLookupFailed):
        error_str = error.original.__doc__
    elif isinstance(error.original, OverflowError):
        error_str = 'Wow buddy, that\'s a big number. Please don\'t do that.'
        database_interface.database.session.rollback()
    elif isinstance(error.original, PlayerNotFound):
        error_str = 'Make sure to use ?register first you ding dong.'
        database_interface.database.session.rollback()
    elif isinstance(error.original, EntryNameNotUniqueError):
        error_str = 'An entry in the database already has that name ding dong.'
        database_interface.database.session.rollback()
    else:
        error_str = bad_error_message.format(ctx.invoked_with, error)

    await bot.send_message(ctx.message.channel, error_str)


@bot.command()
async def test():
    '''
    Checks if the bot is alive.
    '''
    await bot.say('I\'m here you ding dong')


@bot.command(pass_context=True)
async def register(ctx):
    '''
    Registers your Discord and Minecraft account with the the database.
    You must do this before adding entries to the database.
    '''

    try:
        player_name = get_nickname(ctx.message.author)
        database_interface.add_player(player_name, ctx.message.author.id)
    except AttributeError:
        await bot.say('{}, run this command on 24CC whoever you are'.format(ctx.message.author.mention))
        return
    except LocationInitError:
        raise commands.UserInputError

    await bot.say('{}, you have been added to the database.'.format(ctx.message.author.mention))


@bot.command(pass_context=True)
async def addbase(ctx, x_pos: int, y_pos: int, z_pos: int, * args):
    '''
    Adds your base to the database. The name is optional.
        ?addbase [X Coordinate] [Y Coordinate] [Z Coordinate] [Base Name]
    '''

    if len(args) > 0:
        name = args[0]
    else:
        name = '{}\'s_Base'.format(database_interface.find_player_by_discord_uuid(ctx.message.author.id).name)
    try:
        base = database_interface.add_location(ctx.message.author.id, name, x_pos, y_pos, z_pos)
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        await bot.say('{}, a based called {} already exists. You need to specify a different name.'.format(
            ctx.message.author.mention, name))
        return

    await bot.say('{}, your base named **{}** located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))


@bot.command(pass_context=True)
async def addshop(ctx, x_pos: int, y_pos: int, z_pos: int, *args):
    '''
    Adds your shop to the database. The name is optional.
        ?addshop [X Coordinate] [Y Coordinate] [Z Coordinate] [Shop Name]
    '''

    if len(args) > 0:
        name = args[0]
    else:
        name = '{}\'s_Shop'.format(database_interface.find_player_by_discord_uuid(ctx.message.author.id).name)

    try:
        shop = database_interface.add_shop(ctx.message.author.id, name, x_pos, y_pos, z_pos)
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        await bot.say('{}, a shop called **{}** already exists. You need to specify a different name.'.format(
            ctx.message.author.mention, name))
        return

    await bot.say('{}, your shop named **{}** located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, shop.name, shop.pos_to_str()))


@bot.command(pass_context=True)
async def tunnel(ctx, tunnel_color: str, tunnel_number: int, *args):
    '''
    Adds your tunnel to the database.
    The location name is optional. If the location has a tunnel, it is updated.
        ?addtunnel [Tunnel Color] [Tunnel_Number] [Location Name]
    '''

    try:
        if len(args) == 0:
            location_name = None
        else:
            location_name = args[0]

        database_interface.add_tunnel(ctx.message.author.id, tunnel_color, tunnel_number, location_name)
    except EntryNameNotUniqueError:
        await bot.say('{}, you already have one tunnel in the database, please specify a location.'.format(
            ctx.message.author.mention))
        return
    except LocationLookUpError:
        await bot.say('{}, you do not have a location called **{}**.'.format(
            ctx.message.author.mention, args[0]))
        return

    except ValueError:
        raise commands.UserInputError

    await bot.say('{}, your tunnel has been added to the database'.format(ctx.message.author.mention))


@bot.command(pass_context=True)
async def find(ctx, name: str):
    '''
    Finds all the locations a player has in the database.
        ?find [Player name]
    '''

    try:
        loc_list = database_interface.find_location_by_owner_name(name)
        loc_string = loc_list_to_string(loc_list, '{} \n{}')

        await bot.say('{}, **{}** has **{}** locations(s): \n {}'.format(ctx.message.author.mention, name, len(loc_list),
                                                                    loc_string))
    except PlayerNotFound:
        await bot.say('{}, the player **{}** is not in the database'.format(ctx.message.author.mention, name))


@bot.command(pass_context=True)
async def delete(ctx, name: str):
    '''
    Deletes a location from the database.
        ?delete [Location name]
    '''

    try:
        database_interface.delete_location(ctx.message.author.id, name)
        await bot.say('{}, your location named **{}** has been deleted.'.format(ctx.message.author.mention, name))
    except (DeleteEntryError, PlayerNotFound):
        await bot.say('{}, you do not have a location named **{}**.'.format(ctx.message.author.mention, name))


@bot.command(pass_context=True)
async def findaround(ctx, x_pos: int, z_pos: int, * args):
    '''
    Finds all the locations around a certain point.
    The radius defaults to 200 blocks if no value is given.
    Default dimension is overworld.

    ?findaround [X Coordinate] [Z Coordinate] [Optional Flags]

    Optional Flags:
    -r [radius]
    -d [dimension]
    '''

    radius = 200
    dimension = 'Overworld'

    if len(args) == 1:
        radius = args[0]

    flags = get_args_dict(args)

    if len(flags) > 0:
        if '-d' in flags:
            dimension = flags['-d']

    base_list = database_interface.find_location_around(x_pos, z_pos, radius, dimension)

    if len(base_list) != 0:
        base_string = loc_list_to_string(base_list, '{} \n{}')

        await bot.say('{}, there are **{}** locations(s) within **{}** blocks of that point: \n {}'.format(
            ctx.message.author.mention, len(base_list), radius, base_string))
    else:
        await bot.say('{}, there are no locations within {} blocks of that point'
                      .format(ctx.message.author.mention, radius))


@bot.command(pass_context=True)
async def additem(ctx, shop_name: str, item_name: str, quantity: int, diamond_price: int):
    '''
    Adds an item to a shop's inventory.
    Amount for diamond price.

    ?additem [Shop name] [Item Name] [Quantity] [Price]
    '''

    try:
        database_interface.add_item(ctx.message.author.id, shop_name, item_name, diamond_price, quantity)

        await bot.say('{}, **{}** has been added to the inventory of **{}**.'.format(ctx.message.author.mention,
                                                                                     item_name, shop_name))
    except PlayerNotFound:
        await bot.say('{}, you don\'t have any shops in the database.'.format(ctx.message.author.mention))
    except LocationLookUpError:
        await bot.say('{}, you don\'t have any shops named **{}** in the database.'.format(ctx.message.author.mention,
                                                                                          shop_name))


@bot.command(pass_context=True)
async def selling(item_name: str):
    '''
    Lists all the shops selling an item

    ?selling [item]
    '''
    shop_list = database_interface.find_shop_selling_item(item_name)

    shop_list_str = loc_list_to_string(shop_list)
    await bot.say('The following shops sell **{}**: \n {}'.format(item_name, shop_list_str))


@bot.command(pass_context=True)
async def info(ctx, name: str):
    '''
    Displays info about a location.

    If the location is a shop, it displays the shop's inventory.

    ?info [Location Name]
    '''
    try:
        loc = database_interface.find_location_by_name(name)[0]
    except IndexError:
        await bot.say('{}, no location in the database matches {}.'.format(ctx.message.author.mentionm, name))
        return

    await bot.say('{}'.format(loc))

# Helper Functions ************************************************************

def get_nickname(discord_user):
    if discord_user.nick is None:
        name = discord_user.display_name
    else:
        name = discord_user.nick

    if name == 'dootb.in ꙩ ⃤':
        name = 'aeskdar'

    return name


def loc_list_to_string(loc_list, str_format='{}\n{}'):
    loc_string = ''

    for loc in loc_list:
        loc_string = str_format.format(loc_string, loc)

    return loc_string


def get_args_dict(args):
    if len(args) != 0:
        return dict(zip_longest(*[iter(args)] * 2, fillvalue=""))
    else:
        return {}


def create_config():
    config['Discord'] = {'Token': ''}
    config['SQL'] = {'Dialect+Driver': 'test', 'username': '', 'password':'', 'host': '', 'port': '', 'database':''}

    with open('GeoffreyConfig.ini', 'w') as configfile:
        config.write(configfile)

def get_engine_arg(config):
    driver = config['SQL']['Dialect+Driver']
    username = config['SQL']['username']
    password = config['SQL']['password']
    host = config['SQL']['host']
    port = config['SQL']['port']
    database_name = config['SQL']['database']

    engine_args = '{}://{}:{}@{}:{}/{}'

    return engine_args.format(driver, username, password, host, port, database_name)


# Bot Startup ******************************************************************


config = configparser.ConfigParser()
config.read('GeoffreyConfig.ini')

if len(config.sections()) == 0:
    create_config()
    print("GeoffreyConfig.ini generated.")
    quit(0)
else:
    TOKEN = config['Discord']['Token']

    if config['SQL']['dialect+driver'] == 'Test':
        engine_arg = 'sqlite:///temp.db'
    else:
        engine_arg = get_engine_arg(config)

    database_interface = DiscordDatabaseInterface(engine_arg)
    #WebInterface('127.0.0.1', 8081, database)

    bot.run(TOKEN)

