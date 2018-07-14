from discord.ext import commands
from DatabaseModels import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *
import configparser
import sqlite3
#from WebInterface import *

TOKEN = ''
command_prefix = '?'
description = '''
Geoffrey started his life as inside joke none of you will understand.
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
    elif isinstance(error.original.orig, sqlite3.IntegrityError):
        error_str = 'An entry in the database already has that name ding dong.'
        database_interface.database.session.rollback()
    elif isinstance(error.original, sqlite3.IntegrityError):
        error_str = 'Oof, the fuck did you do? Try the command again but be less of a ding dong with it.'
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
    Registers your discord and minecraft account with the the database. You must do this before adding entries to
    the database.
    '''

    player_name = get_nickname(ctx.message.author)

    try:
        database_interface.add_player(player_name, ctx.message.author.id)
    except LocationInitError:
        raise commands.UserInputError

    await bot.say('{}, you have been added to the database.'.format(ctx.message.author.mention))


@bot.command(pass_context=True)
async def addbase(ctx, name: str, x_pos: int, y_pos: int, z_pos: int, * args):
    '''
    Add your base to the database.
     The tunnel address is optional.
     The default dimension is the overworld. Valid options: overworld, nether, end
     ?addbase [Base Name] [X Coordinate] [Y Coordinate] [Z Coordinate] [Tunnel Color]
        [Tunnel Position] [Side] [Dimension]
    '''

    player_name = get_nickname(ctx.message.author)

    try:
        base = database_interface.add_location(ctx.message.author.id, name, x_pos, y_pos, z_pos, args)
    except LocationInitError:
        raise commands.UserInputError

    await bot.say('{}, your base named **{}** located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, base.name, base.pos_to_str()))

@bot.command(pass_context=True)
async def addshop(ctx, name: str, x_pos: int, y_pos: int, z_pos: int, * args):
    '''
    Adds a shop to the database.
     The tunnel address is optional.
     The default dimension is the overworld. Valid options: overworld, nether, end
     ?addbase [Base Name] [X Coordinate] [Y Coordinate] [Z Coordinate] [Tunnel Color]
        [Tunnel Position] [Side] {Dimension]
    '''

    player_name = get_nickname(ctx.message.author)

    try:
        shop = database_interface.add_shop(ctx.message.author.id, name, x_pos, y_pos, z_pos, args)
    except LocationInitError:
        raise commands.UserInputError

    await bot.say('{}, your shop named **{}** located at {} has been added'
                  ' to the database.'.format(ctx.message.author.mention, shop.name, shop.pos_to_str()))


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

    player_name = get_nickname(ctx.message.author)
    try:
        database_interface.delete_base(player_name, name)
        await bot.say('{}, your location named **{}** has been deleted.'.format(ctx.message.author.mention, name))
    except (DeleteEntryError, PlayerNotFound):
        await bot.say('{}, you do not have a location named **{}**.'.format(ctx.message.author.mention, name))


@bot.command(pass_context=True)
async def findaround(ctx, x_pos: int, z_pos: int, * args):
    '''
    Finds all the locations around a certain point that are registered in the database
    The Radius argument defaults to 200 blocks if no value is given
        ?findbasearound [X Coordinate] [Z Coordinate] [Radius]
    '''

    radius = 200
    if len(args) > 0:
        try:
            radius = int(args[0])
        except ValueError:
            raise commands.UserInputError

    base_list = database_interface.find_location_around(x_pos, z_pos, radius)

    if len(base_list) != 0:
        base_string = loc_list_to_string(base_list, '{} \n{}')

        await bot.say('{}, there are {} locations(s) within {} blocks of that point: \n {}'.format(
            ctx.message.author.mention, len(base_list), radius, base_string))
    else:
        await bot.say('{}, there are no locations within {} blocks of that point'
                      .format(ctx.message.author.mention, radius))


@bot.command(pass_context=True)
async def additem(ctx, shop_name: str, item_name: str, amount: int, diamond_price: int):
    '''
    Adds an item to a shop's inventory. Amount for diamond price.
        ?additem [Shop name] [Item Name] [Amount] [Price]
    '''

    try:
        player_name = get_nickname(ctx.message.author)
        database_interface.add_item(ctx.message.author.id, shop_name, item_name, diamond_price, amount)

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
    await bot.say('The following shops sell {}: \n {}'.format(item_name, shop_list_str))


@bot.command(pass_context=True)
async def shopinfo(ctx, shop_name: str):
    '''
    Lists the information and inventory of a shop
        ?shopinfo [Shop Name]
    '''
    shop = database_interface.find_shop_by_name(shop_name)[0]
    inv_list = database_interface.get_shop_inventory(shop)

    item_list = ''
    for item in inv_list:
        item_list = item_list + '{}\n'.format(item.__str__())

    await bot.say('{} \n Inventory:\n {}'.format(shop.__str__(), item_list))

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

