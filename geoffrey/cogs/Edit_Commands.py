from discord.ext import commands

from geoffrey.BotErrors import *
from geoffrey.DiscordHelperFunctions import *


class Edit_Commands:
    """
    Commands for editing your stuff in Geoffrey.
    """
    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def edit_pos(self, ctx, x_pos: int, y_pos: int, *args):
        """
        Edits the position of a location
            ?edit_pos [X Coordinate] [Z Coordinate] [Location Name]
        """
        loc = get_name(args)
        try:
            loc_str = self.bot.bot_commands.edit_pos(x_pos, y_pos, loc, discord_uuid=ctx.message.author.id)

            await self.bot.say(
                '{}, the following location has been updated: \n\n{}'.format(ctx.message.author.mention, loc_str))
        except LocationLookUpError:
            await self.bot.say('{}, you do not have a location called **{}**.'.format(
                ctx.message.author.mention, loc))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def edit_tunnel(self, ctx, tunnel_color: str, tunnel_number: int, *args):
        """
        Edits the tunnel of a location
            ?edit_tunnel [Tunnel Color] [Tunnel Number] [Location Name]
        """
        loc = get_name(args)
        try:
            loc_str = self.bot.bot_commands.edit_tunnel(tunnel_color, tunnel_number, loc,
                                                        discord_uuid=ctx.message.author.id)

            await self.bot.say(
                '{}, the following location has been updated: \n\n{}'.format(ctx.message.author.mention, loc_str))
        except LocationLookUpError:
            await self.bot.say('{}, you do not have a location called **{}**.'.format(
                ctx.message.author.mention, loc))
        except InvalidTunnelError:
            await self.bot.say(
                '{}, **{}** is an invalid tunnel color.'.format(ctx.message.author.mention, tunnel_color))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def edit_name(self, ctx, new_name: str, current_name: str):
        """
        Edits the name of a location
         IF A NAME HAS SPACES IN IT YOU NEED TO WRAP IT IN QUOTATION MARKS. eg. "Cool Shop 123"
            ?edit_name [New Name] [Current Name]
        """
        try:
            loc_str = self.bot.bot_commands.edit_name(new_name, current_name, discord_uuid=ctx.message.author.id)

            await self.bot.say(
                '{}, the following location has been updated: \n\n{}'.format(ctx.message.author.mention, loc_str))
        except LocationLookUpError:
            await self.bot.say('{}, you do not have a location called **{}**.'.format(
                ctx.message.author.mention, current_name))


def setup(bot):
    bot.add_cog(Edit_Commands(bot))
