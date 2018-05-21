import discord
from discord.ext import commands

TOKEN = 'MTgzMDMyMDE5MTk2ODM3ODg4.DeRsbQ.UmFJ_7bjmIuIp8jIk6AkUnQ49a0'

command_prefix = '?'
description = '''Geoffrey is an inside joke none of you will understand, at 
least he knows where your bases are.'''

bot = commands.Bot(command_prefix=command_prefix , description=description)

playing = 'Waiting for you to type ''?'''

@bot.event
async def on_ready():
	print('GeoffreyBot')
	print('Username: ' + bot.user.name)
	print('ID: ' + bot.user.id)

@bot.command()
async def test():
	'''Check if the bot is alive'''
	await bot.say('I\'m here you ding dong')

@bot.command(pass_context=True)
async def addBase(ctx, * args):
	if (len(args) > 0) :
		try:
			name = args[0]
			x = int(args[1])
			z = int(args[2])
			await bot.say('{}, your base named {} located at (x={},z={}) has been added to the database.'.format(ctx.message.author.mention, name, x, z))
		except ValueError:
			await bot.say('Invalid syntax, try again (?addbase [name] [x coord] [z coord])')
			
	else :
		await bot.say('Allows you to add your base location to the database. Syntax: ?addbase [Base Name] [X Cordinate] [Z Cordinate]')
	
bot.run(TOKEN)