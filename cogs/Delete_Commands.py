from discord.ext import commands
from BotErrors import *
from DiscordHelperFunctions import *
from bot import bot_commands


@commands.cooldown(5, 60, commands.BucketType.user)
class Delete_Commands:
    '''
    Commands to help Geoffrey forget.

    *You must use ?register before using any of these commands!*
    '''

    def __init__(self, bot):
        self.bot = bot

    @commands.command(pass_context=True)
    async def delete(self, ctx, *args):
        '''
        Deletes a location from the database.
            ?delete [Location name]
        '''
        loc = get_name(args)
        try:
            if loc is None:
                raise commands.UserInputError

            bot_commands.delete(loc, discord_uuid=ctx.message.author.id)
            await self.bot.say(
                '{}, your location named **{}** has been deleted.'.format(ctx.message.author.mention, loc))
        except (DeleteEntryError, PlayerNotFound):
            await self.bot.say('{}, you do not have a location named **{}**.'.format(ctx.message.author.mention, loc))

    @commands.command(pass_context=True)
    async def delete_item(self, ctx, item: str, *args):
        '''
            Deletes an item listing from a shop inventory

            ?delete_name [Item] [Shop Name]
        '''

        shop = get_name(args)
        try:
            bot_commands.delete_item(item, shop, discord_uuid=ctx.message.author.id)

            await self.bot.say('{}, **{}** has been removed from the inventory of **{}**.'.
                          format(ctx.message.author.mention, item, shop))
        except LocationLookUpError:
            if shop is None:
                await self.bot.say('{}, you do have any shops in the database.'.format(ctx.message.author.mention))
            else:
                await self.bot.say('{}, you do not have a shop called **{}**.'.format(ctx.message.author.mention, shop))
        except EntryNameNotUniqueError:
            await self.bot.say('{}, you have more than one shop in the database, please specify a shop name.'
                          .format(ctx.message.author.mention))
        except DeleteEntryError:
            if shop is not None:
                await self.bot.say('{}, **{}** does not sell **{}**.'.format(ctx.message.author.mention, shop, item))
            else:
                await self.bot.say('{}, your shop does not sell **{}**.'.format(ctx.message.author.mention, item))


def setup(bot):
    bot.add_cog(Delete_Commands(bot))
