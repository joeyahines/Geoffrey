from discord.ext import commands
from Commands import *
from BotErrors import *
from MinecraftAccountInfoGrabber import *
from BotConfig import *
import threading

command_prefix = '?'
description = '''
Geoffrey (pronounced JOFF-ree) started his life as an inside joke none of you will understand.
At some point, she was to become an airhorn bot. Now, they know where your stuff is.

Please respect Geoffrey, the bot is very sensitive.

If have a suggestion or if something is borked, you can PM my ding dong of a creator ZeroHD.

*You must use ?register before adding things to Geoffrey*
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
    elif isinstance(error.original, NoPermissionError):
        error_str = 'You don\'t have permission for that cool command.'
    elif isinstance(error.original, UsernameLookupFailed):
        error_str = error.original.__doc__
    elif isinstance(error.original, PlayerNotFound):
        error_str = 'Make sure to use ?register first you ding dong.'
    elif isinstance(error.original, EntryNameNotUniqueError):
        error_str = 'An entry in the database already has that name ding dong.'
    elif isinstance(error.original, DatabaseValueError):
        error_str = 'Use a shorter name or a smaller value, dong ding.'
    elif isinstance(error.original, NotOnServerError):
        error_str = 'Command needs to be run on 24CC. Run this command there whoever you are.'.format()
    else:
        error_str = bad_error_message.format(ctx.invoked_with, error)

    await bot.send_message(ctx.message.channel, '{} **Error Running Command:** {}'.format(ctx.message.author.mention,
                                                                                          error_str))

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

extensions = ['Add_Commands', 'Delete_Commands', 'Edit_Commands', 'Search_Commands', 'Admin_Commands']

if __name__ == '__main__':
    for extension in extensions:
        try:
            bot.load_extension(extension)
        except Exception as e:
            print('Failed to load extension {}'.format(extension))
    update_user_names(bot_commands)
    bot.run(TOKEN)


