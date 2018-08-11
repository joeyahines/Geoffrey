from discord.ext import commands
from BotErrors import *
from BotConfig import bot_config
from DiscordHelperFunctions import *
from Geoffrey import bot_commands


def check_mod(user):
    try:
        for role in user.roles:
            if role.id == bot_config.bot_mod:
                return True
    except AttributeError:
        raise NotOnServerError

    return False


class Admin_Commands:
    '''
    Commands for cool people only.
    '''

    def __init__(self, bot):
        self.bot = bot

    async def error(self, error, ctx):
        if isinstance(error.original, PlayerNotFound):
            error_str = 'that player is not in the database.'
        elif isinstance(error.original, DeleteEntryError):
            error_str = 'that player does not have a location by that name.'
        else:
            return

        await self.bot.send_message(ctx.message.channel, '{}, {}'.format(ctx.message.author.mention, error_str))

    @commands.command(pass_context=True)
    async def test(self, ctx):
        '''
        Checks if the bot is alive.
        '''
        if check_mod(ctx.message.author):
            await self.bot.say('I\'m here you ding dong')
        else:
            raise NoPermissionError

    @commands.group(pass_context=True)
    async def mod(self, ctx):

        if check_mod(ctx.message.author):
            if ctx.invoked_subcommand is None:
                await self.bot.say('{}, invalid sub-command for command **mod**.'.format(ctx.message.author.mention))
        else:
            raise NoPermissionError

    @mod.command(pass_context=True)
    async def delete(self, ctx, discord_uuid: str, location_name: str):
        bot_commands.delete(location_name, discord_uuid=discord_uuid)
        await self.bot.say('{}, **{}** has been deleted.'.format(ctx.message.author.mention, location_name))

    @delete.error
    async def delete_error(self, error, ctx):
        await self.error(error, ctx)

    @mod.command(pass_context=True)
    async def edit(self, ctx, discord_uuid: str, new_name: str, current_name: str):
        bot_commands.edit_name(new_name, current_name, discord_uuid=discord_uuid)
        await self.bot.say('{}, **{}** has been rename to **{}**.'.format(ctx.message.author.mention, current_name,
                                                                          new_name))

    @edit.error
    async def edit_error(self, error, ctx):
        await self.error(error, ctx)

    @mod.command(pass_context=True)
    async def update_mc_uuid(self, ctx, discord_uuid: str, mc_uuid: str):
        bot_commands.update_mc_uuid(discord_uuid, mc_uuid)
        await self.bot.say('{}, **{}** has been updated.'.format(ctx.message.author.mention, discord_uuid))

    @update_mc_uuid.error
    async def update_mc_uuid_error(self, error, ctx):
        await self.error(error, ctx)

    @mod.command(pass_context=True)
    async def update_discord_uuid(self, ctx, current_discord_uuid: str, new_discord_uuid: str):
        bot_commands.update_mc_uuid(current_discord_uuid, new_discord_uuid)
        await self.bot.say('{}, user **{}** has been updated.'.format(ctx.message.author.mention, current_discord_uuid))

    @update_discord_uuid.error
    async def update_discord_uuid_error(self, error, ctx):
        await self.error(error, ctx)

    @mod.command(pass_context=True)
    async def update_mc_name(self, ctx, discord_uuid: str, mc_name: str):
        bot_commands.update_mc_name(discord_uuid, mc_name)
        await self.bot.say('{}, user **{}** has been renamed.'.format(ctx.message.author.mention, mc_name))

    @update_mc_name.error
    async def update_mc_name_error(self, error, ctx):
        await self.error(error, ctx)



def setup(bot):
    bot.add_cog(Admin_Commands(bot))