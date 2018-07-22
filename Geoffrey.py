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

    session = database_interface.database.Session()
    try:
        player_name = get_nickname(ctx.message.author)
        database_interface.add_player(session, player_name, ctx.message.author.id)
    except AttributeError:
        await bot.say('{}, run this command on 24CC whoever you are'.format(ctx.message.author.mention))
        return
    except LocationInitError:
        raise commands.UserInputError
    session.close()
    await bot.say('{}, you have been added to the database.'.format(ctx.message.author.mention))


@bot.command(pass_context=True)
async def addbase(ctx, x_pos: int, z_pos: int, * args):
    '''
    Adds your base to the database. The name is optional.
        ?addbase [X Coordinate] [Y Coordinate] [Z Coordinate] [Base Name]
    '''
    session = database_interface.database.Session()
    if len(args) > 0:
        name = ' '.join(args)
    else:
        name = '{}\'s_Base'.format(database_interface.find_player_by_discord_uuid(session, ctx.message.author.id).name)
    try:
        base = database_interface.add_location(session, ctx.message.author.id, name, x_pos, z_pos)
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        await bot.say('{}, a based called {} already exists. You need to specify a different name.'.format(
            ctx.message.author.mention, name))
        return

    await bot.say('{}, your base named **{}** located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))

    session.close()


@bot.command(pass_context=True)
async def addshop(ctx, x_pos: int, z_pos: int, *args):
    '''
    Adds your shop to the database. The name is optional.
        ?addshop [X Coordinate] [Y Coordinate] [Z Coordinate] [Shop Name]
    '''
    session = database_interface.database.Session()
    if len(args) > 0:
        name = ' '.join(args)
    else:
        name = '{}\'s_Shop'.format(database_interface.find_player_by_discord_uuid(session, ctx.message.author.id).name)

    try:
        shop = database_interface.add_shop(session, ctx.message.author.id, name, x_pos, z_pos)
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        await bot.say('{}, a shop called **{}** already exists. You need to specify a different name.'.format(
            ctx.message.author.mention, name))
        return

    await bot.say('{}, your shop named **{}** located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, shop.name, shop.pos_to_str()))

    session.close()


@bot.command(pass_context=True)
async def tunnel(ctx, tunnel_color: str, tunnel_number: int, *args):
    '''
    Adds your tunnel to the database.
    The location name is optional. If the location has a tunnel, it is updated.
        ?addtunnel [Tunnel Color] [Tunnel_Number] [Location Name]
    '''
    session = database_interface.database.Session()
    try:
        if len(args) == 0:
            location_name = None
        else:
            location_name = ' '.join(args)

        database_interface.add_tunnel(session, ctx.message.author.id, tunnel_color, tunnel_number, location_name)
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

    session.close()


@bot.command(pass_context=True)
async def find(ctx, search: str):
    '''
    Finds all the locations and tunnels matching the search term
        ?find [Search]
    '''
    session = database_interface.database.Session()
    try:
        result = database_interface.search_all_fields(session, search)

        await bot.say('{}, The following entries match **{}**:\n{}'.format(ctx.message.author.mention, search, result))
    except LocationLookUpError:
        await bot.say('{}, no matches **{}** were found in the database'.format(ctx.message.author.mention, search))

    session.close()


@bot.command(pass_context=True)
async def delete(ctx, * args):
    '''
    Deletes a location from the database.
        ?delete [Location name]
    '''
    session = database_interface.database.Session()
    try:
        name = ' '.join(args)
        database_interface.delete_location(session, ctx.message.author.id, name)
        await bot.say('{}, your location named **{}** has been deleted.'.format(ctx.message.author.mention, name))
    except (DeleteEntryError, PlayerNotFound):
        await bot.say('{}, you do not have a location named **{}**.'.format(ctx.message.author.mention, name))

    session.close()


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
    session = database_interface.database.Session()
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

        base_list = database_interface.find_location_around(session, x_pos, z_pos, radius, dimension)

        if len(base_list) != 0:
            base_string = loc_list_to_string(base_list, '{} \n{}')

            await bot.say('{}, there are **{}** locations(s) within **{}** blocks of that point: \n {}'.format(
                ctx.message.author.mention, len(base_list), radius, base_string))
        else:
            await bot.say('{}, there are no locations within {} blocks of that point'
                          .format(ctx.message.author.mention, radius))
    except ValueError:
        raise commands.UserInputError

    session.close()


@bot.command(pass_context=True)
async def additem(ctx, item_name: str, quantity: int, diamond_price: int, * args):
    '''
    Adds an item to a shop's inventory.
    Quantity for Diamond Price.

    ?additem [Item Name] [Quantity] [Price] [Shop name]
    '''
    session = database_interface.database.Session()
    try:
        shop_list = database_interface.find_shop_by_owner_uuid(session, ctx.message.author.id)

        if len(shop_list) == 1:
            shop_name = shop_list[0].name
        else:
            if len(args) == 0:
                raise LocationInitError
            else:
                shop_name = ' '.join(args)

            database_interface.add_item(session, ctx.message.author.id, shop_name, item_name, diamond_price, quantity)
        await bot.say('{}, **{}** has been added to the inventory of **{}**.'.format(ctx.message.author.mention,
                                                                                     item_name, shop_name))
    except PlayerNotFound:
        await bot.say('{}, you don\'t have any shops in the database.'.format(ctx.message.author.mention))
    except LocationInitError:
        await bot.say('{}, you have more than one shop in the database, please specify a shop name.'
                      .format(ctx.message.author.mention))
    except LocationLookUpError:
        await bot.say('{}, you don\'t have any shops named **{}** in the database.'.format(ctx.message.author.mention,
                                                                                          shop_name))

    session.close()


@bot.command(pass_context=True)
async def selling(ctx, item_name: str):
    '''
    Lists all the shops selling an item

    ?selling [item]
    '''
    session = database_interface.database.Session()
    shop_list = database_interface.find_shop_selling_item(session, item_name)

    shop_list_str = loc_list_to_string(shop_list)
    await bot.say('{}, the following shops sell **{}**: \n{}'.format(ctx.message.author.mention, item_name,
                                                                      shop_list_str))

    session.close()


@bot.command(pass_context=True)
async def info(ctx, * args):
    '''
    Displays info about a location.

    If the location is a shop, it displays the shop's inventory.

    ?info [Location Name]
    '''
    session = database_interface.database.Session()
    try:
        name = ' '.join(args)
        loc = database_interface.find_location_by_name(session, name)[0]
    except IndexError:
        await bot.say('{}, no locations in the database match {}.'.format(ctx.message.author.mention, name))
        return

    await bot.say('{}'.format(loc.full_str()))

    session.close()

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

