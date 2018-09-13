from discord.ext import commands

from geoffrey.BotErrors import *
from geoffrey.DiscordHelperFunctions import *


class Delete_Commands:
    """
    Commands to help Geoffrey forget.

    *You must use ?register before using any of these commands!*
    """

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def delete(self, ctx, *args):
        """
        Deletes a location from the database
            ?delete [Location name]
        """
        loc = get_name(args)
        try:
            if loc is None:
                raise commands.UserInputError

            self.bot.bot_commands.delete(loc, discord_uuid=ctx.message.author.id)
            await ctx.send(
                '{}, your location named **{}** has been deleted.'.format(ctx.message.author.mention, loc))
        except (DeleteEntryError, PlayerNotFound):
            await ctx.send('{}, you do not have a location named **{}**.'.format(ctx.message.author.mention, loc))

    @commands.command(pass_context=True)
    async def delete_item(self, ctx, item: str, *args):
        """
            Deletes an item listing from a shop inventory

            ?delete_name [Item] [Shop Name]
        """

        shop = get_name(args)
        try:
            shop_name = self.bot.bot_commands.delete_item(item, shop, discord_uuid=ctx.message.author.id)

            await ctx.send('{}, **{}** has been removed from the inventory of **{}**.'.
                           format(ctx.message.author.mention, item, shop_name))
        except LocationLookUpError:
            if shop is None:
                await ctx.send('{}, you do have any shops in the database.'.format(ctx.message.author.mention))
            else:
                await ctx.send('{}, you do not have a shop called **{}**.'.format(ctx.message.author.mention, shop))
        except EntryNameNotUniqueError:
            await ctx.send('{}, you have more than one shop in the database, please specify a shop name.'
                           .format(ctx.message.author.mention))
        except DeleteEntryError:
            if shop is not None:
                await ctx.send('{}, **{}** does not sell **{}**.'.format(ctx.message.author.mention, shop, item))
            else:
                await ctx.send('{}, your shop does not sell **{}**.'.format(ctx.message.author.mention, item))


def setup(bot):
    bot.add_cog(Delete_Commands(bot))
