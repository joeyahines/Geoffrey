from discord import Game
from discord.ext import commands

from geoffrey.BotErrors import *
from geoffrey.DiscordHelperFunctions import get_name


def check_mod(user, admin_users):
    try:
        for role in user.roles:
            if str(role.id) in admin_users:
                return True
    except AttributeError:
        raise NotOnServerError

    return False


class Admin_Commands:
    """
    Commands for cool people only.
    """

    def __init__(self, bot):
        self.bot = bot

    async def error(self, ctx, error):
        if isinstance(error, PlayerNotFound):
            error_str = 'that player is not in the database.'
        elif isinstance(error, DeleteEntryError):
            error_str = 'that player does not have a location by that name.'
        else:
            error_str = 'the bot encountered the following error: {}'.format(error.__str__())

        await ctx.send('{}, {}'.format(ctx.message.author.mention, error_str))

    @commands.command(pass_context=True)
    async def test(self, ctx):
        """
        Checks if the bot is alive.
        """
        if check_mod(ctx.message.author, self.bot.admin_users):
            await ctx.send('I\'m here you ding dong')
        else:
            raise NoPermissionError

    @commands.group(pass_context=True)
    async def mod(self, ctx):
        """
        Bot moderation tools.
        """
        if check_mod(ctx.message.author, self.bot.admin_users):
            if ctx.invoked_subcommand is None:
                await ctx.send('{}, invalid sub-command for command **mod**.'.format(ctx.message.author.mention))
        else:
            raise NoPermissionError

    @mod.command(pass_context=True)
    async def delete(self, ctx, discord_uuid: str, location_name: str):
        """
        Deletes a location in the database.
        """
        self.bot.bot_commands.delete(location_name, discord_uuid=discord_uuid)
        await ctx.send('{}, **{}** has been deleted.'.format(ctx.message.author.mention, location_name))

    @delete.error
    async def delete_error(self, ctx, error):
        await self.error(ctx, error)

    @mod.command(pass_context=True)
    async def edit_name(self, ctx, discord_uuid: str, new_name: str, current_name: str):
        """
        Edits the name of a location in the database.
        """
        self.bot.bot_commands.edit_name(new_name, current_name, discord_uuid=discord_uuid)
        await ctx.send('{}, **{}** has been rename to **{}**.'.format(ctx.message.author.mention, current_name,
                                                                          new_name))

    @edit_name.error
    async def edit_error(self, ctx, error):
        await self.error(ctx, error)

    @mod.command(pass_context=True)
    async def update_mc_uuid(self, ctx, discord_uuid: str, mc_uuid: str):
        """
        Updates a user's MC UUID.
        """
        self.bot.bot_commands.update_mc_uuid(discord_uuid, mc_uuid)
        await ctx.send('{}, **{}** has been updated.'.format(ctx.message.author.mention, discord_uuid))

    @update_mc_uuid.error
    async def update_mc_uuid_error(self, ctx, error):
        await self.error(ctx, error)

    @mod.command(pass_context=True)
    async def update_discord_uuid(self, ctx, current_discord_uuid: str, new_discord_uuid: str):
        """
        Updates a user's Discord UUID.
        """
        self.bot.bot_commands.update_mc_uuid(current_discord_uuid, new_discord_uuid)
        await ctx.send('{}, user **{}** has been updated.'.format(ctx.message.author.mention, current_discord_uuid))

    @update_discord_uuid.error
    async def update_discord_uuid_error(self, ctx, error):
        await self.error(ctx, error)

    @mod.command(pass_context=True)
    async def update_mc_name(self, ctx, discord_uuid: str):
        """
        Updates a user's MC name to the current name on the MC UUID.
        """
        self.bot.bot_commands.update_mc_name(discord_uuid)
        await ctx.send('{}, user **{}**\'s MC name has update.'.format(ctx.message.author.mention, discord_uuid))

    @update_mc_name.error
    async def update_mc_name_error(self, ctx, error):
        await self.error(ctx, error)

    @mod.command(pass_context=True)
    async def status(self, ctx, *args):
        """
        Updates "playing [game]" status of the bot.
        """
        status = get_name(args)
        await self.bot.change_presence(activity=Game(status))
        await ctx.send('{}, status has been changed'.format(ctx.message.author.mention))


def setup(bot):
    bot.add_cog(Admin_Commands(bot))
