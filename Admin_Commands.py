from discord.ext import commands
from BotErrors import *
from DiscordHelperFunctions import *
from Geoffrey import bot_commands


class Admin_Commands:
    '''
    Commands for cool people only.
    '''

    def __init__(self, bot):
        self.bot = bot

    def check_mod(self, user):
        try:
            if ("admin" in [y.name.lower() for y in user.roles]) | \
                    ("mod" in [y.name.lower() for y in user.roles]):
                return True
            else:
                return False
        except AttributeError:
            raise NotOnServerError

    @commands.command(pass_context=True)
    async def test(self, ctx):
        '''
        Checks if the bot is alive.
        '''
        if self.check_mod(ctx.message.author):
            await self.bot.say('I\'m here you ding dong')
        else:
            raise NoPermissionError


def setup(bot):
    bot.add_cog(Admin_Commands(bot))