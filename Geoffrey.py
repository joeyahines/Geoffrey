from discord.ext import commands
from Commands import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *
from itertools import zip_longest
from BotConfig import *
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
    elif isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.UserInputError):
        error_str = 'Invalid syntax for **{}** you ding dong, please read ?help {}.'\
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


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command()
async def test():
    '''
    Checks if the bot is alive.
    '''
    await bot.say('I\'m here you ding dong')


@commands.cooldown(5, 60, commands.BucketType.user)
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


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def add_base(ctx, x_pos: int, z_pos: int, * args):
    '''
    Adds your base to the database.
        The name is optional.
        ?add_base [X Coordinate] [Z Coordinate] [Base Name]
    '''

    name = get_name(args)

    try:
        base = bot_commands.add_base(x_pos, z_pos, base_name=name, discord_uuid=ctx.message.author.id)
        await bot.say('{}, your base has been added to the database: \n\n{}'.format(ctx.message.author.mention, base))
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        if name is None:
            await bot.say('{}, you already have one base in the database, you need to specify a base'
                          ' name'.format(ctx.message.author.mention))
        else:
            await bot.say('{}, a base called **{}** already exists. You need to specify a different name.'.format(
                ctx.message.author.mention, name))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def add_shop(ctx, x_pos: int, z_pos: int, *args):
    '''
    Adds your shop to the database.
        The name is optional.
        ?add_shop [X Coordinate] [Z Coordinate] [Shop Name]
    '''

    name = get_name(args)

    try:
        shop = bot_commands.add_shop(x_pos, z_pos, shop_name=name, discord_uuid=ctx.message.author.id)
        await bot.say('{}, your shop has been added to the database: \n\n{}'.format(ctx.message.author.mention, shop))
    except LocationInitError:
        raise commands.UserInputError
    except EntryNameNotUniqueError:
        if name is None:
            await bot.say('{}, you already have one shop in the database, you need to specify a shop name'.format(
                ctx.message.author.mention))
        else:
            await bot.say('{}, a shop called **{}** already exists. You need to specify a different name.'.format(
                ctx.message.author.mention, name))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def add_tunnel(ctx, tunnel_color: str, tunnel_number: int, *args):
    '''
    Adds your tunnel to the database.
        ?tunnel [Tunnel Color] [Tunnel Number] [Location Name]
    '''

    loc_name = get_name(args)
    try:
        bot_commands.add_tunnel(tunnel_color, tunnel_number, discord_uuid=ctx.message.author.id, location_name=loc_name)
        await bot.say('{}, your tunnel has been added to the database'.format(ctx.message.author.mention))
    except LocationLookUpError:
        await bot.say('{}, you do not have a location called **{}**.'.format(
            ctx.message.author.mention, loc_name))
    except LocationHasTunnelError:
        await bot.say('{}, **{}** already has a tunnel.'.format(ctx.message.author.mention, loc_name))
    except TunnelInitError:
        await bot.say('{}, invalid tunnel color.'.format(ctx.message.author.mention))
    except EntryNameNotUniqueError:
        await bot.say('{}, you have more than one location, you need to specify a location.'
                      .format(ctx.message.author.mention))
    except InvalidTunnelError:
        await bot.say('{}, **{}** is an invalid tunnel color.'.format(ctx.message.author.mention, tunnel_color))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def find(ctx, * args):
    '''
    Finds all the locations and tunnels matching the search term
        ?find [Search]
    '''
    search = get_name(args)
    try:

        if search is None:
            raise commands.UserInputError

        result = bot_commands.find(search)

        await bot.say('{}, The following entries match **{}**:\n{}'.format(ctx.message.author.mention, search, result))
    except LocationLookUpError:
        await bot.say('{}, no matches to **{}** were found in the database.'.format(ctx.message.author.mention, search))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def tunnel(ctx, player: str):
    '''
    Finds all the tunnels a player owns.
        ?tunnel [Player]
    '''
    try:
        result = bot_commands.tunnel(player)

        await bot.say('{}, **{}** owns the following tunnels: \n{}'.format(ctx.message.author.mention, player, result))
    except LocationLookUpError:
        await bot.say('{}, no tunnels for the player **{}** were found in the database/'
                      .format(ctx.message.author.mention, player))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def delete(ctx, * args):
    '''
    Deletes a location from the database.
        ?delete [Location name]
    '''
    loc = get_name(args)
    try:
        if loc is None:
            raise commands.UserInputError

        bot_commands.delete(loc, discord_uuid=ctx.message.author.id)
        await bot.say('{}, your location named **{}** has been deleted.'.format(ctx.message.author.mention, loc))
    except (DeleteEntryError, PlayerNotFound):
        await bot.say('{}, you do not have a location named **{}**.'.format(ctx.message.author.mention, loc))


@bot.command(pass_context=True)
@commands.cooldown(5, 60, commands.BucketType.user)
async def find_around(ctx, x_pos: int, z_pos: int, * args):
    '''
    Finds all the locations around a certain point.
    The radius defaults to 200 blocks if no value is given.
    Default dimension is overworld.

    ?find_around [X Coordinate] [Z Coordinate] [Radius] [Optional Flags]

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

        base_string = bot_commands.find_around(x_pos, z_pos, radius, dimension)

        if len(base_string) != 0:
            await bot.say('{}, the following locations(s) within **{}** blocks of that point: \n {}'.format(
                ctx.message.author.mention, radius, base_string))
        else:
            await bot.say('{}, there are no locations within {} blocks of that point'
                          .format(ctx.message.author.mention, radius))
    except InvalidDimError:
        await bot.say('{}, {} is an invalid dimension.'.format(ctx.message.author.mention, dimension))


@bot.command(pass_context=True)
@commands.cooldown(5, 60, commands.BucketType.user)
async def add_item(ctx, item_name: str, quantity: int, diamond_price: int, * args):
    '''
    Adds an item to a shop's inventory.
    Quantity for Diamond Price.

    ?additem [Item Name] [Quantity] [Price] [Shop name]
    '''
    shop_name = get_name(args)
    try:
        bot_commands.add_item(item_name, quantity, diamond_price, shop_name=shop_name,
                              discord_uuid=ctx.message.author.id)
        await bot.say('{}, **{}** has been added to the inventory of your shop.'.format(ctx.message.author.mention,
                                                                                        item_name))
    except PlayerNotFound:
        await bot.say('{}, you don\'t have any shops in the database.'.format(ctx.message.author.mention))
    except LocationInitError:
        await bot.say('{}, you have more than one shop in the database, please specify a shop name.'
                      .format(ctx.message.author.mention))
    except LocationLookUpError:
        await bot.say('{}, you don\'t have any shops named **{}** in the database.'.format(ctx.message.author.mention,
                                                                                           shop_name))


@commands.cooldown(5, 60, commands.BucketType.user)
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
        await bot.say('{}, no shop sells **{}**.'.format(ctx.message.author.mention, item_name))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def info(ctx, * args):
    '''
    Displays info about a location.

    If the location is a shop, it displays the shop's inventory.

    ?info [Location Name]
    '''
    loc = get_name(args)
    try:

        if loc is None:
            raise commands.UserInputError

        info_str = bot_commands.info(loc)
        await bot.say(info_str)
    except IndexError:
        await bot.say('{}, no locations in the database match {}.'.format(ctx.message.author.mention, loc))
        return


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def edit_pos(ctx, x_pos: int, y_pos: int, * args):
    '''
        Edits the position of a location

        ?edit_pos [X Coordinate] [Z Coordinate] [Location Name]
    '''
    loc = get_name(args)
    try:
        loc_str = bot_commands.edit_pos(x_pos, y_pos, loc, discord_uuid=ctx.message.author.id)

        await bot.say('{}, the following location has been updated: \n\n{}'.format(ctx.message.author.mention, loc_str))
    except LocationLookUpError:
        await bot.say('{}, you do not have a location called **{}**.'.format(
            ctx.message.author.mention, loc))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def edit_tunnel(ctx, tunnel_color: str, tunnel_number: int, * args):
    '''
        Edits the tunnel of a location

        ?edit_tunnel [Tunnel Color] [Tunnel Number] [Location Name]
    '''
    loc = get_name(args)
    try:
        loc_str = bot_commands.edit_tunnel(tunnel_color, tunnel_number, loc, discord_uuid=ctx.message.author.id)

        await bot.say('{}, the following location has been updated: \n\n{}'.format(ctx.message.author.mention, loc_str))
    except LocationLookUpError:
        await bot.say('{}, you do not have a location called **{}**.'.format(
            ctx.message.author.mention, loc))
    except InvalidTunnelError:
        await bot.say('{}, **{}** is an invalid tunnel color.'.format(ctx.message.author.mention, tunnel_color))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def edit_name(ctx, new_name: str, current_name: str):
    '''
        Edits the name of a location

        IF A NAME HAS SPACES IN IT YOU NEED TO WRAP IT IN QUOTATION MARKS. ie "Cool Shop 123"
        ?edit_name [New Name] [Current Name]
    '''
    try:
        loc_str = bot_commands.edit_name(new_name, current_name, discord_uuid=ctx.message.author.id)

        await bot.say('{}, the following location has been updated: \n\n{}'.format(ctx.message.author.mention, loc_str))
    except LocationLookUpError:
        await bot.say('{}, you do not have a location called **{}**.'.format(
            ctx.message.author.mention, current_name))


@commands.cooldown(5, 60, commands.BucketType.user)
@bot.command(pass_context=True)
async def delete_item(ctx, item: str, * args):
    '''
        Deletes an item listing from a shop inventory

        ?delete_name [Item] [Shop Name]
    '''

    shop = get_name(args)
    try:
        bot_commands.delete_item(item, shop, discord_uuid=ctx.message.author.id)

        await bot.say('{}, **{}** has been removed from the inventory of **{}**.'.
                      format(ctx.message.author.mention, item, shop))
    except LocationLookUpError:
        await bot.say('{}, you do not have a shop called **{}**.'.format(ctx.message.author.mention, shop))
    except DeleteEntryError:
        await bot.say('{}, **{}** does not sell **{}**.'.format(ctx.message.author.mention, shop, item))

# Helper Functions ************************************************************

def get_name(args):
    if len(args) > 0:
        name = ' '.join(args)
    else:
        name = None

    return name

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
        return dict(zip_longest(*[iter(args)] * 2, fillvalue=" "))
    else:
        return {}


def update_user_names(bot_commands):
    threading.Timer(600, update_user_names, [bot_commands]).start()
    session = bot_commands.interface.database.Session()
    print("Updating MC usernames...")
    player_list = session.query(Player).all()

    for player in player_list:
        player.name = grab_playername(player.mc_uuid)

    session.commit()

    session.close()


# Bot Startup ******************************************************************

config = read_config()

TOKEN = config['Discord']['Token']

engine_arg = get_engine_arg(config)

bot_commands = Commands(engine_arg)

update_user_names(bot_commands)

bot.run(TOKEN)



