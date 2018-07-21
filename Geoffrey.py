from discord.ext import commands
from DatabaseModels import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *
from itertools import zip_longest
from BotConfig import *

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
    elif isinstance(error.original, StringTooLong):
        error_str = 'Use a shorter name you, dong ding.'
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
async def addbase(ctx, x_pos: int, z_pos: int, * args):
    '''
    Adds your base to the database. The name is optional.
        ?addbase [X Coordinate] [Y Coordinate] [Z Coordinate] [Base Name]
    '''

    if len(args) > 0:
        name = args[0]
    else:
        name = '{}\'s_Base'.format(database_interface.find_player_by_discord_uuid(ctx.message.author.id).name)
    try:
        base = database_interface.add_location(ctx.message.author.id, name, x_pos, z_pos)
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        await bot.say('{}, a based called {} already exists. You need to specify a different name.'.format(
            ctx.message.author.mention, name))
        return

    await bot.say('{}, your base named **{}** located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))


@bot.command(pass_context=True)
async def addshop(ctx, x_pos: int, z_pos: int, *args):
    '''
    Adds your shop to the database. The name is optional.
        ?addshop [X Coordinate] [Y Coordinate] [Z Coordinate] [Shop Name]
    '''

    if len(args) > 0:
        name = args[0]
    else:
        name = '{}\'s_Shop'.format(database_interface.find_player_by_discord_uuid(ctx.message.author.id).name)

    try:
        shop = database_interface.add_shop(ctx.message.author.id, name, x_pos, z_pos)
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
async def find(ctx, search: str):
    '''
    Finds all the locations and tunnels matching the search term
        ?find [Search]
    '''

    try:
        result = database_interface.search_all_fields(search)

        await bot.say('{}, The following entries match **{}**:\n{}'.format(ctx.message.author.mention, search, result))
    except LocationLookUpError:
        await bot.say('{}, no matches **{}** were found in the database'.format(ctx.message.author.mention, search))


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

    ?findaround [X Coordinate] [Z Coordinate] [Radius] [Optional Flags]

    Optional Flags:
    -d [dimension]
    '''

    radius = 200
    dimension = 'Overworld'

    try:
        if len(args) > 0:
            if args[0] == '-d':
                dimension = args[1]
            else:
                radius = int(args[0])

                if len(args) > 1:
                    if args[1] == '-d':
                        dimension = args[2]

        base_list = database_interface.find_location_around(x_pos, z_pos, radius, dimension)

        if len(base_list) != 0:
            base_string = loc_list_to_string(base_list, '{} \n{}')

            await bot.say('{}, there are **{}** locations(s) within **{}** blocks of that point: \n {}'.format(
                ctx.message.author.mention, len(base_list), radius, base_string))
        else:
            await bot.say('{}, there are no locations within {} blocks of that point'
                          .format(ctx.message.author.mention, radius))
    except ValueError:
        raise commands.UserInputError


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
async def selling(ctx, item_name: str):
    '''
    Lists all the shops selling an item

    ?selling [item]
    '''
    shop_list = database_interface.find_shop_selling_item(item_name)

    shop_list_str = loc_list_to_string(shop_list)
    await bot.say('{}, the following shops sell **{}**: \n{}'.format(ctx.message.author.mention, item_name,
                                                                      shop_list_str))


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
        await bot.say('{}, no locations in the database match {}.'.format(ctx.message.author.mention, name))
        return

    await bot.say('{}'.format(loc.full_str()))

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


# Bot Startup ******************************************************************

config = read_config()

TOKEN = config['Discord']['Token']

engine_arg = get_engine_arg(config)

database_interface = DiscordDatabaseInterface(engine_arg)

bot.run(TOKEN)

