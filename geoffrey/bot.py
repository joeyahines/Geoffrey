import asyncio
import logging

from discord import Game
from discord.ext import commands
from discord.utils import oauth_url
from sqlalchemy.exc import OperationalError

from BotConfig import bot_config
from BotErrors import *
from Commands import Commands
from DatabaseModels import Player
from MinecraftAccountInfoGrabber import *

logger = logging.getLogger(__name__)

description = '''
Geoffrey (pronounced JOFF-ree) started his life as an inside joke none of you will understand.
At some point, she was to become an airhorn bot. Now, they know where your stuff is.

Please respect Geoffrey, the bot is very sensitive.

If have a suggestion or if something is borked, you can PM my ding dong of a creator ZeroHD.

*You must use ?register before adding things to Geoffrey*
'''

bad_error_message = 'OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The admins at our ' \
                    'headquarters are working VEWY HAWD to fix this! (Error in command {})'

extensions = ['cogs.Add_Commands',
              'cogs.Delete_Commands',
              'cogs.Edit_Commands',
              'cogs.Search_Commands',
              'cogs.Admin_Commands']

bot = commands.Bot(command_prefix=bot_config.prefix, description=description, case_insensitive=True)

try:
    bot_commands = Commands()
except OperationalError:
    logger.info('Could not connect to MySQL server.')


@bot.event
async def on_ready():
    logger.info("%s Online, ID: %s", bot.user.name, bot.user.id)
    info = await bot.application_info()
    url = oauth_url(info.id)
    logger.info("Bot url: %s", url)
    await bot.change_presence(game=Game(name=bot_config.status))


@bot.event
async def on_command(command, ctx):
    if ctx.invoked_subcommand is None:
        subcommand = ""
    else:
        subcommand = ":" + ctx.invoked_subcommand

    logger.info("User %s, used command %s%s with context: %s", ctx.message.author, command, subcommand, ctx.args)


@bot.event
async def on_command_error(error, ctx):
    if hasattr(ctx, 'cog'):
        if "Admin_Commands" in ctx.cog.__str__():
            return
    if isinstance(error, commands.CommandNotFound):
        return
    elif isinstance(error, commands.CommandOnCooldown):
        return
    elif isinstance(error, commands.UserInputError):
        error_str = 'Invalid syntax for **{}** you ding dong:' \
            .format(ctx.invoked_with, ctx.invoked_with)

        pages = bot.formatter.format_help_for(ctx, ctx.command)
        for page in pages:
            error_str = error_str + '\n' + page

    elif isinstance(error.original, NoPermissionError):
        error_str = 'You don\'t have permission for that cool command.'
    elif isinstance(error.original, UsernameLookupFailed):
        error_str = 'Your user name was not found, either Mojang is having a fucky wucky ' \
                    'or your nickname is not set correctly. *stares at the Mods*'
    elif isinstance(error.original, PlayerNotFound):
        error_str = 'Make sure to use ?register first you ding dong.'
    elif isinstance(error.original, EntryNameNotUniqueError):
        error_str = 'An entry in the database already has that name you ding dong.'
    elif isinstance(error.original, DatabaseValueError):
        error_str = 'Use a shorter name or a smaller value, dong ding.'
    elif isinstance(error.original, NotOnServerError):
        error_str = 'Command needs to be run on 24CC. Run this command there whoever you are.'.format()
    elif isinstance(error.original, OperationalError):
        await send_error_message('Error connecting to the MySQL server, is it offline?')
        error_str = 'Database connection issue, looks like some admin has to fix something.'.format()
    else:
        await send_error_message('Geoffrey encountered unhandled exception: {}. Context:'.format(error, ctx.args))

        logger.error("Geoffrey encountered unhandled exception: %s", error)
        error_str = bad_error_message.format(ctx.invoked_with)

    await bot.send_message(ctx.message.channel, '{} **Error Running Command:** {}'.format(ctx.message.author.mention,
                                                                                          error_str))


async def send_error_message(msg):
    for user_id in bot_config.error_users:
        user = await bot.get_user_info(user_id)
        await bot.send_message(user, msg)


async def username_update():
    await bot.wait_until_ready()
    while not bot.is_closed:
        session = bot_commands.interface.database.Session()
        try:
            logger.info("Updating MC usernames...")
            session = bot_commands.interface.database.Session()
            player_list = session.query(Player).all()
            for player in player_list:
                player.name = grab_playername(player.mc_uuid)

            session.commit()
            logger.info("Username update done.")

        except UsernameLookupFailed:
            logger.info("Username lookup error.")
            session.rollback()
        except OperationalError:
            await send_error_message('Error connecting to the MySQL server, is it offline?')
            logger.info("MySQL connection error")
        finally:
            session.close()
            await asyncio.sleep(600)


def start_bot():
    try:
        Commands()
        for extension in extensions:
            try:
                bot.load_extension(extension)
            except Exception as e:
                logger.info('Failed to load extension {}'.format(extension))
                raise e
        bot.loop.create_task(username_update())
        logger.info('Logging into Discord...')
        bot.run(bot_config.token)
    except KeyboardInterrupt:
        logger.info("Bot received keyboard interrupt")
    except Exception as e:
        logger.info('Bot encountered the following unhandled exception %s', e)
    finally:
        bot.loop.stop()
        logger.info("Bot shutting down...")