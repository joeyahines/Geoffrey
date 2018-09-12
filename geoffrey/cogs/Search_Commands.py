from discord.ext import commands

from geoffrey.BotErrors import *
from geoffrey.DiscordHelperFunctions import *


class Search_Commands:
    """
    Commands to find stuff.
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def find(self, ctx, *args):
        """
        Finds all the locations and tunnels matching the search term
            ?find [Search]
        """
        search = get_name(args)
        try:

            if search is None:
                raise commands.UserInputError

            result = self.bot.bot_commands.find(search)

            await ctx.send(
                '{}, The following entries match **{}**:\n{}'.format(ctx.message.author.mention, search, result))
        except LocationLookUpError:
            await ctx.send(
                '{}, no matches to **{}** were found in the database.'.format(ctx.message.author.mention, search))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def tunnel(self, ctx, player: str):
        """
        Finds all the tunnels a player owns.
            ?tunnel [Player]
        """
        try:
            result = self.bot.bot_commands.tunnel(player)

            await ctx.send(
                '{}, **{}** owns the following tunnels: \n{}'.format(ctx.message.author.mention, player, result))
        except LocationLookUpError:
            await ctx.send('{}, no tunnels for **{}** were found in the database.'
                               .format(ctx.message.author.mention, player))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def find_around(self, ctx, x_pos: int, z_pos: int, *args):
        """
        Finds all the locations around a certain point.
        The radius defaults to 200 blocks if no value is given.
        Default dimension is overworld.
            ?find_around [X Coordinate] [Z Coordinate] [Radius] [Optional Flags]

            Optional Flags:
            -d [dimension]
        """
        radius = 200
        dimension = 'Overworld'

        try:
            if len(args) > 0:
                if args[0] == '-d':
                    dimension = args[1]
                    if len(args) > 1:
                        radius = int(args[2])
                else:
                    radius = int(args[0])

                    if len(args) > 1:
                        if args[1] == '-d':
                            dimension = args[2]

            base_string = self.bot.bot_commands.find_around(x_pos, z_pos, radius, dimension)

            if len(base_string) != 0:
                await ctx.send('{}, the following locations(s) within **{}** blocks of that point: \n {}'.format(
                    ctx.message.author.mention, radius, base_string))
            else:
                await ctx.send('{}, there are no locations within {} blocks of that point'
                                   .format(ctx.message.author.mention, radius))
        except ValueError:
            await ctx.send(
                '{}, invalid radius, the radius must be a whole number.'.format(ctx.message.author.mention,
                                                                                radius))
        except InvalidDimError:
            await ctx.send('{}, {} is an invalid dimension.'.format(ctx.message.author.mention, dimension))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def selling(self, ctx, item_name: str):
        """
        Lists all the shops selling an item
            ?selling [item]
        """
        try:
            result = self.bot.bot_commands.selling(item_name)
            await ctx.send(
                '{}, the following shops sell **{}**: \n{}'.format(ctx.message.author.mention, item_name, result))
        except ItemNotFound:
            await ctx.send('{}, no shop sells **{}**.'.format(ctx.message.author.mention, item_name))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def info(self, ctx, *args):
        """
        Displays info about a location.
        If the location is a shop, it displays the shop's inventory.
            ?info [Location Name]
        """
        loc = get_name(args)
        try:

            if loc is None:
                raise commands.UserInputError

            info_str = self.bot.bot_commands.info(loc)
            await ctx.send(info_str)
        except IndexError:
            await ctx.send('{}, no locations in the database match **{}**.'.format(ctx.message.author.mention, loc))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def me(self, ctx):
        """
        Displays all your locations in the database
        """
        try:
            loc_str = self.bot.bot_commands.me(discord_uuid=ctx.message.author.id)
            await ctx.send('{}, here are your locations in the database: \n {}'.format(ctx.message.author.mention,
                                                                                           loc_str))
        except PlayerNotFound:
            await ctx.send('{}, you don\'t have any locations in the database.'.format(ctx.message.author.mention))


def setup(bot):
    bot.add_cog(Search_Commands(bot))
