import asyncio
import logging

from discord import Game
from discord.ext import commands
from discord.utils import oauth_url
from sqlalchemy.exc import OperationalError
import logging.handlers as handlers
from sys import stdout
from os import path

from geoffrey.BotConfig import *
from geoffrey.BotErrors import *
from geoffrey.Commands import Commands
from geoffrey.DatabaseModels import Player
from geoffrey.MinecraftAccountInfoGrabber import *

logger = logging.getLogger(__name__)

description = '''
Geoffrey (pronounced JOFF-ree) started his life as an inside joke none of you will understand.
At some point, she was to become an airhorn bot. Now, they know where your stuff is.

Please respect Geoffrey, the bot is very sensitive.

If have a suggestion or if something is borked, you can PM my ding dong of a creator ZeroHD.

*You must use ?register before adding things to Geoffrey*

Basic Use Case:
Adding your first first base:
?add_base 500 300
Adding your second base:
?add_base 500 900 Cool Base Name
'''

bad_error_message = 'OOPSIE WOOPSIE!! Uwu We made a fucky wucky!! A wittle fucko boingo! The admins at our ' \
                    'headquarters are working VEWY HAWD to fix this! (Error in command {})'

extensions = ['geoffrey.cogs.Add_Commands',
              'geoffrey.cogs.Delete_Commands',
              'geoffrey.cogs.Edit_Commands',
              'geoffrey.cogs.Search_Commands',
              'geoffrey.cogs.Admin_Commands']


class GeoffreyBot(commands.Bot):
    def __init__(self, config):
        super().__init__(command_prefix=config.prefix, description=description, pm_help=True, case_insensitive=True)
        self.error_users = config.error_users
        self.admin_users = config.bot_mod
        self.special_users = config.special_name_list
        self.bot_commands = Commands(config)
        self.default_status = config.status

        for extension in extensions:
            try:
                self.load_extension(extension)
            except Exception as e:
                logger.info('Failed to load extension {}'.format(extension))
                raise e

    async def on_ready(self):
        logger.info("%s Online, ID: %s", self.user.name, self.user.id)
        info = await self.application_info()
        url = oauth_url(info.id)
        logger.info("Bot url: %s", url)
        await self.change_presence(activity=Game(self.default_status))

    async def on_command(self, ctx):
        if ctx.invoked_subcommand is None:
            subcommand = ""
        else:
            subcommand = ":" + ctx.invoked_subcommand.__str__()

        logger.info("User %s, used command %s%s with context: %s", ctx.message.author, ctx.command, subcommand,
                    ctx.args)

    async def on_command_error(self, ctx, error):
        error_str = ''
        if hasattr(ctx, 'cog'):
            if "Admin_Commands" in ctx.cog.__str__():
                return
        if hasattr(error, 'original'):
            if isinstance(error.original, NoPermissionError):
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
                await self.send_error_message('Error connecting to the MySQL server, is it offline?')
                error_str = 'Database connection issue, looks like some admin has to fix something.'.format()
        elif isinstance(error, commands.CommandOnCooldown):
            return
        elif isinstance(error, commands.UserInputError):
            error_str = 'Invalid syntax for **{}** you ding dong:' \
                .format(ctx.invoked_with, ctx.invoked_with)

            pages = await self.formatter.format_help_for(ctx, ctx.command)
            for page in pages:
                error_str = error_str + '\n' + page
        elif isinstance(error, commands.CommandNotFound):
            return

        if error_str is '':
            await self.send_error_message(
                'Geoffrey encountered unhandled exception: {}. Context:'.format(error, ctx.args))
            error_str = bad_error_message.format(ctx.invoked_with)

        logger.error("Geoffrey encountered exception: %s", error)

        await ctx.message.channel.send('{} **Error Running Command:** {}'.format(
            ctx.message.author.mention, error_str))

    async def send_error_message(self, msg):
        for user_id in self.error_users:
            user = await self.get_user_info(user_id)
            await user.send(msg)


async def username_update(bot):
    await bot.wait_until_ready()
    while not bot.is_closed:
        session = bot.bot_commands.interface.database.Session()
        try:
            logger.info("Updating MC usernames...")
            session = bot.bot_commands.interface.database.Session()
            player_list = session.query(Player).all()
            for player in player_list:
                player.name = grab_playername(player.mc_uuid)

            session.commit()
            logger.info("Username update done.")

        except UsernameLookupFailed:
            logger.info("Username lookup error.")
            session.rollback()
        except OperationalError:
            await bot.send_error_message('Error connecting to the MySQL server, is it offline?')
            logger.info("MySQL connection error")
        finally:
            session.close()
            await asyncio.sleep(600)


def setup_logging(config):
    discord_logger = logging.getLogger('discord')
    discord_logger.setLevel(logging.INFO)
    sql_logger = logging.getLogger('sqlalchemy.engine')
    sql_logger.setLevel(logging.INFO)
    bot_info_logger = logging.getLogger('geoffrey.bot')
    bot_info_logger.setLevel(logging.INFO)
    log_path = path.abspath(config.log_path)

    handler = handlers.TimedRotatingFileHandler(filename="{}/Geoffrey.log".format(log_path), when='D',
                                                interval=config.rotation_duration, backupCount=config.count,
                                                encoding='utf-8')

    handler.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    console = logging.StreamHandler(stdout)

    console.setFormatter(logging.Formatter('%(asctime)s:%(levelname)s:%(name)s: %(message)s'))

    discord_logger.addHandler(handler)
    sql_logger.addHandler(handler)
    bot_info_logger.addHandler(handler)
    bot_info_logger.addHandler(console)


def start_bot(config_path="{}/GeoffreyConfig.ini".format(path.dirname(path.abspath(__file__)))):
    bot = None
    try:
        bot_config = get_config(config_path)

        bot = GeoffreyBot(bot_config)

        setup_logging(bot_config)

        bot.loop.create_task(username_update(bot))
        bot.run(bot_config.token)

    except KeyboardInterrupt:
        logger.info("Bot received keyboard interrupt")
    except Exception as e:
        logger.info('Bot encountered the following unhandled exception %s', e)
    finally:
        if bot is not None:
            bot.loop.stop()
        logger.info("Bot shutting down...")
