from discord.ext import commands
from Commands import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *
from itertools import zip_longest
from BotConfig import *
import time
import threading

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
    elif isinstance(error.original, UsernameLookupFailed):
        error_str = error.original.__doc__
    elif isinstance(error.original, PlayerNotFound):
        error_str = 'Make sure to use ?register first you ding dong.'
    elif isinstance(error.original, EntryNameNotUniqueError):
        error_str = 'An entry in the database already has that name ding dong.'
    elif isinstance(error.original, DatabaseValueError):
        error_str = 'Use a shorter name or a smaller value, dong ding.'
    else:
        error_str = bad_error_message.format(ctx.invoked_with, error)

    await bot.send_message(ctx.message.channel, '{} **Error Running Command:** {}'.format(ctx.message.author.mention,
                                                                                          error_str))


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
        bot_commands.register(player_name, ctx.message.author.id)
        await bot.say('{}, you have been added to the database.'.format(ctx.message.author.mention))
    except AttributeError:
        await bot.say('{}, run this command on 24CC whoever you are'.format(ctx.message.author.mention))
    except LocationInitError:
        raise commands.UserInputError
    except PlayerInDB:
        await bot.say('{}, you are already in the database. Ding dong.'.format(ctx.message.author.mention))



@bot.command(pass_context=True)
async def addbase(ctx, x_pos: int, z_pos: int, * args):
    '''
    Adds your base to the database.
        The name is optional.
        ?addbase [X Coordinate] [Y Coordinate] [Z Coordinate] [Base Name]
    '''
    if len(args) > 0:
        name = ' '.join(args)
    else:
        name = None

    try:
        base = bot_commands.addbase(x_pos, z_pos, base_name=name, discord_uuid=ctx.message.author.id)
        await bot.say('{}, your base has been added to the database: {}'.format(ctx.message.author.mention, base))
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        if name is None:
            await bot.say('{}, you already have one base in the database, you need to specify a base'
                          ' name'.format(ctx.message.author.mention))
        else:
            await bot.say('{}, a base called **{}** already exists. You need to specify a different name.'.format(
                ctx.message.author.mention, name))


@bot.command(pass_context=True)
async def addshop(ctx, x_pos: int, z_pos: int, *args):
    '''
    Adds your shop to the database.
        The name is optional.
        ?addshop [X Coordinate] [Y Coordinate] [Z Coordinate] [Shop Name]
    '''
    if len(args) > 0:
        name = ' '.join(args)
    else:
        name = None

    try:
        shop = bot_commands.addshop(x_pos, z_pos, shop_name=name, discord_uuid=ctx.message.author.id)
        await bot.say('{}, your shop has been added to the database: {}'.format(ctx.message.author.mention, shop))
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        if name is None:
            await bot.say('{}, you already have one shop in the database, you need to specify a shop name'.format(
                ctx.message.author.mention))
        else:
            await bot.say('{}, a shop called **{}** already exists. You need to specify a different name.'.format(
                ctx.message.author.mention, name))

@bot.command(pass_context=True)
async def tunnel(ctx, tunnel_color: str, tunnel_number: int, *args):
    '''
    Adds your tunnel to the database.
        The location name is optional. If the location has a tunnel, it is updated.
        ?tunnel [Tunnel Color] [Tunnel Number] [Location Name]
    '''
    try:
        if len(args) > 0:
            location_name = ' '.join(args)
        else:
            location_name = None

        bot_commands.tunnel(tunnel_color, tunnel_number, discord_uuid=ctx.message.author.id, location_name=location_name)
        await bot.say('{}, your tunnel has been added to the database'.format(ctx.message.author.mention))
    except EntryNameNotUniqueError:
        await bot.say('{}, you already have one tunnel in the database, please specify a location.'.format(
            ctx.message.author.mention))
        return
    except LocationLookUpError:
        await bot.say('{}, you do not have a location called **{}**.'.format(
            ctx.message.author.mention, args[0]))
    except TunnelInitError:
        await bot.say('{}, invalid tunnel color.'.format(ctx.message.author.mention))
    except InvalidTunnelError:
        await bot.say('{}, {} is an invalid tunnel color.'.format(ctx.message.author.mention, tunnel_color))


@bot.command(pass_context=True)
async def find(ctx, * args):
    '''
    Finds all the locations and tunnels matching the search term
        ?find [Search]
    '''
    try:
        search = ' '.join(args)
        result = bot_commands.find(search)

        await bot.say('{}, The following entries match **{}**:\n{}'.format(ctx.message.author.mention, search, result))
    except LocationLookUpError:
        await bot.say('{}, no matches to **{}** were found in the database'.format(ctx.message.author.mention, search))

@bot.command(pass_context=True)
async def delete(ctx, * args):
    '''
    Deletes a location from the database.
        ?delete [Location name]
    '''
    try:
        name = ' '.join(args)
        bot_commands.delete(name, discord_uuid=ctx.message.author.id)
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

    try:
        radius = 200
        dimension = 'Overworld'

        if len(args) > 0:
            if args[0] == '-d':
                dimension = args[1]
            else:
                radius = int(args[0])

                if len(args) > 1:
                    if args[1] == '-d':
                        dimension = args[2]

        base_string = bot_commands.findaround(x_pos, z_pos, radius, dimension)

        if len(base_string) != 0:
            await bot.say('{}, the following locations(s) within **{}** blocks of that point: \n {}'.format(
                ctx.message.author.mention, radius, base_string))
        else:
            await bot.say('{}, there are no locations within {} blocks of that point'
                          .format(ctx.message.author.mention, radius))
    except InvalidDimError:
        await bot.say('{}, {} is an invalid dimension.'.format(ctx.message.author.mention, dimension))


@bot.command(pass_context=True)
async def additem(ctx, item_name: str, quantity: int, diamond_price: int, * args):
    '''
    Adds an item to a shop's inventory.
    Quantity for Diamond Price.

    ?additem [Item Name] [Quantity] [Price] [Shop name]
    '''
    try:
        if len(args) > 0:
            shop_name = ' '.join(args)
        else:
            shop_name = None

        bot_commands.additem(item_name, quantity, diamond_price, shop_name=shop_name)
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


@bot.command(pass_context=True)
async def selling(ctx, item_name: str):
    '''
    Lists all the shops selling an item

    ?selling [item]
    '''
    try:
        result = bot_commands.selling(item_name)
        await bot.say('{}, the following shops sell **{}**: \n{}'.format(ctx.message.author.mention, item_name, result))
    except ItemNotFound:
        await bot.say('{}, bo shops sell {}'.format(ctx.message.author.mention, item_name))


@bot.command(pass_context=True)
async def info(ctx, * args):
    '''
    Displays info about a location.

    If the location is a shop, it displays the shop's inventory.

    ?info [Location Name]
    '''
    try:
        if len(args) > 0:
            name = ' '.join(args)
        else:
            raise commands.UserInputError

        info_str = bot_commands.info(name)
        await bot.say(info_str)
    except IndexError:
        await bot.say('{}, no locations in the database match {}.'.format(ctx.message.author.mention, name))
        return

# Helper Functions ************************************************************


def get_nickname(discord_user):
    if discord_user.nick is None:
        name = discord_user.display_name
    else:
        name = discord_user.nick

    if name == 'dootb.in ꙩ ⃤':
        name = 'aeskdar'

    return name


def get_args_dict(args):
    if len(args) != 0:
        return dict(zip_longest(*[iter(args)] * 2, fillvalue=""))
    else:
        return {}


def update_user_names(bot_commands):
    threading.Timer(600, update_user_names, [bot_commands]).start()
    session = bot_commands.interface.database.Session()

    player_list = session.query(Player).all()

    for player in player_list:
        player.name = grab_playername(player.mc_uuid)

    print("Updating MC usernames...")
    session.commit()

    session.close()


# Bot Startup ******************************************************************

config = read_config()

TOKEN = config['Discord']['Token']

engine_arg = get_engine_arg(config)

bot_commands = Commands(engine_arg)

update_user_names(bot_commands)

bot.run(TOKEN)


