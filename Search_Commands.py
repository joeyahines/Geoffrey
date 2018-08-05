from discord.ext import commands
from BotErrors import *
from DiscordHelperFunctions import *
from Geoffrey import bot_commands


@commands.cooldown(5, 60, commands.BucketType.user)
class Search_Commands:
    '''
    Commands to find stuff.
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def find(self, ctx, * args):
        '''
        Finds all the locations and tunnels matching the search term
            ?find [Search]
        '''
        search = get_name(args)
        try:

            if search is None:
                raise commands.UserInputError

            result = bot_commands.find(search)

            await self.bot.say('{}, The following entries match **{}**:\n{}'.format(ctx.message.author.mention, search, result))
        except LocationLookUpError:
            await self.bot.say('{}, no matches to **{}** were found in the database.'.format(ctx.message.author.mention, search))


    @commands.command(pass_context=True)
    async def tunnel(self, ctx, player: str):
        '''
        Finds all the tunnels a player owns.
            ?tunnel [Player]
        '''
        try:
            result = bot_commands.tunnel(player)

            await self.bot.say('{}, **{}** owns the following tunnels: \n{}'.format(ctx.message.author.mention, player, result))
        except LocationLookUpError:
            await self.bot.say('{}, no tunnels for **{}** were found in the database.'
                          .format(ctx.message.author.mention, player))


    @commands.command(pass_context=True)
    async def find_around(self, ctx, x_pos: int, z_pos: int, * args):
        '''
        Finds all the locations around a certain point.
        The radius defaults to 200 blocks if no value is given.
        Default dimension is overworld.

        ?find_around [X Coordinate] [Z Coordinate] [Radius] [Optional Flags]

        Optional Flags:
        -d [dimension]
        '''
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

            base_string = bot_commands.find_around(x_pos, z_pos, radius, dimension)

            if len(base_string) != 0:
                await self.bot.say('{}, the following locations(s) within **{}** blocks of that point: \n {}'.format(
                    ctx.message.author.mention, radius, base_string))
            else:
                await self.bot.say('{}, there are no locations within {} blocks of that point'
                              .format(ctx.message.author.mention, radius))
        except ValueError:
            await self.bot.say('{}, invalid radius, the radius must be a whole number.'.format(ctx.message.author.mention,
                                                                                          radius))
        except InvalidDimError:
            await self.bot.say('{}, {} is an invalid dimension.'.format(ctx.message.author.mention, dimension))

    @commands.command(pass_context=True)
    async def selling(self, ctx, item_name: str):
        '''
        Lists all the shops selling an item

        ?selling [item]
        '''
        try:
            result = bot_commands.selling(item_name)
            await self.bot.say('{}, the following shops sell **{}**: \n{}'.format(ctx.message.author.mention, item_name, result))
        except ItemNotFound:
            await self.bot.say('{}, no shop sells **{}**.'.format(ctx.message.author.mention, item_name))

    @commands.command(pass_context=True)
    async def info(self, ctx, * args):
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
            await self.bot.say(info_str)
        except IndexError:
            await self.bot.say('{}, no locations in the database match **{}**.'.format(ctx.message.author.mention, loc))


def setup(bot):
    bot.add_cog(Search_Commands(bot))
