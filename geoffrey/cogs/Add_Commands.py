from discord.ext import commands

from geoffrey.BotErrors import *
from geoffrey.DiscordHelperFunctions import *


@commands.cooldown(5, 60, commands.BucketType.user)
class Add_Commands:
    """
    Commands for adding things to Geoffrey.
    *You must use ?register before using any of these commands!*
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def register(self, ctx):
        """
        Registers your Discord and Minecraft account with the the database
        You must do this before adding entries to the database.
        """

        try:
            player_name = get_nickname(ctx.message.author, self.bot.special_users)
            self.bot.bot_commands.register(player_name, ctx.message.author.id)
            await ctx.send('{}, you have been added to the database. Use ?help to see all the commands this bot can do.'
                           .format(ctx.message.author.mention))
        except AttributeError:
            raise NotOnServerError
        except PlayerInDBError:
            await ctx.send('{}, you are already in the database. Ding dong.'.format(ctx.message.author.mention))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def add_base(self, ctx, x_pos: int, z_pos: int, *args):
        """
        Adds your base to the database. The base name is optional if this your first base
            ?add_base [X Coordinate] [Z Coordinate] [Base Name]
        """

        name = get_name(args)

        try:
            base = self.bot.bot_commands.add_base(x_pos, z_pos, base_name=name, discord_uuid=ctx.message.author.id)
            await ctx.send(
                '{}, your base has been added to the database: \n\n{}'.format(ctx.message.author.mention, base))
        except LocationInitError:
            raise commands.UserInputError
        except EntryNameNotUniqueError:
            if name is None:
                await ctx.send('{}, you already have one base in the database, you need to specify a base'
                               ' name'.format(ctx.message.author.mention))
            else:
                await ctx.send(
                    '{}, a base called **{}** already exists. You need to specify a different name.'.format(
                        ctx.message.author.mention, name))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def add_shop(self, ctx, x_pos: int, z_pos: int, *args):
        """
        Adds your shop to the database. The name is shop optional if this your first shop
            ?add_shop [X Coordinate] [Z Coordinate] [Shop Name]
        """

        name = get_name(args)

        try:
            shop = self.bot.bot_commands.add_shop(x_pos, z_pos, shop_name=name, discord_uuid=ctx.message.author.id)
            await ctx.send(
                '{}, your shop has been added to the database: \n\n{}'.format(ctx.message.author.mention, shop))
        except LocationInitError:
            raise commands.UserInputError
        except EntryNameNotUniqueError:
            if name is None:
                await ctx.send(
                    '{}, you already have one shop in the database, you need to specify a shop name'.format(
                        ctx.message.author.mention))
            else:
                await ctx.send(
                    '{}, a shop called **{}** already exists. You need to specify a different name.'.format(
                        ctx.message.author.mention, name))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def add_tunnel(self, ctx, tunnel_direction: str, tunnel_number: int, *args):
        """
        Adds your tunnel to the database. If you only have one location, you do not need to specify a location name

        Directions: North South East West
            ?tunnel [Tunnel Direction] [Tunnel Number] [Location Name]
        """

        loc_name = get_name(args)
        try:
            self.bot.bot_commands.add_tunnel(tunnel_direction, tunnel_number, discord_uuid=ctx.message.author.id,
                                             location_name=loc_name)
            await ctx.send('{}, your tunnel has been added to the database'.format(ctx.message.author.mention))
        except LocationLookUpError:
            await ctx.send('{}, you do not have a location called **{}**.'.format(
                ctx.message.author.mention, loc_name))
        except NoLocationsInDatabase:
            await ctx.send('{}, you do not have a location in the database.'.format(
                ctx.message.author.mention, loc_name))
        except LocationHasTunnelError:
            await ctx.send('{}, **{}** already has a tunnel.'.format(ctx.message.author.mention, loc_name))
        except TunnelInitError:
            await ctx.send('{}, invalid tunnel direction.'.format(ctx.message.author.mention))
        except EntryNameNotUniqueError:
            await ctx.send('{}, you have more than one location, you need to specify a location.'
                           .format(ctx.message.author.mention))
        except InvalidTunnelError:
            await ctx.send(
                '{}, **{}** is an invalid tunnel direction.'.format(ctx.message.author.mention, tunnel_direction))

    @commands.command(pass_context=True)
    @commands.cooldown(5, 60, commands.BucketType.user)
    async def add_item(self, ctx, item_name: str, quantity: int, diamond_price: int, *args):
        """
        Adds an item to a shop's inventory. If you have one shop, the shop name is not required

        Quantity for Diamond Price. eg. 32 Dirt for 1D. If the item name has spaces in wrap in in quotes eg "Silk Touch"
            ?add_item [Item Name] [Quantity] [Price] [Shop name]
        """
        shop_name = get_name(args)
        try:
            self.bot.bot_commands.add_item(item_name, quantity, diamond_price, shop_name=shop_name,
                                           discord_uuid=ctx.message.author.id)
            await ctx.send(
                '{}, **{}** has been added to the inventory of your shop.'.format(ctx.message.author.mention,
                                                                                  item_name))
        except NoLocationsInDatabase:
            await ctx.send('{}, you don\'t have any shops in the database.'.format(ctx.message.author.mention))
        except LocationInitError:
            await ctx.send('{}, you have more than one shop in the database, please specify a shop name.'
                           .format(ctx.message.author.mention))
        except LocationLookUpError:
            await ctx.send(
                '{}, you don\'t have any shops named **{}** in the database.'.format(ctx.message.author.mention,
                                                                                     shop_name))


def setup(bot):
    bot.add_cog(Add_Commands(bot))
