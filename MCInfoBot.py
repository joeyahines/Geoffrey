import discord
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import sessionmaker

engine = create_engine('sqlite:///:memory:', echo=True)
SQL_Base = declarative_base()

TOKEN = ''
command_prefix = '?'
description = '''Geoffrey is an inside joke none of you will understand, at 
least he knows where your bases are.'''

bot = commands.Bot(command_prefix=command_prefix , description=description)

class Location(SQL_Base):
	__tablename__ = 'Locations'
	name = Column(String, primary_key=True)
	x = Column(Integer)
	y = Column(Integer)
	z = Column(Integer)
	
	def __init__(self,args) :
		self.name = args[0]
		self.x = int(args[1])
		self.y = int(args[2])
		self.z = int(args[3])

	def  posToStr(self) :
		return '(x=' + str(self.x) + ', y=' + str(self.y) + ', z=' + str(self.z) + ')' 
		
	def __repr__(self):
		return "(name= {}, pos={})".format(self.name,posToStr)
		
SQL_Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

			
#Bot Commands ******************************************************************		
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
async def addbase(ctx, * args):
	'''Add your base to the database.'''
	if (len(args) == 4) :
		try:
			base = Location(args)
			session.add(base)
			await bot.say('{}, your base named {} located at {} has been added'
				' to the database.'.format(ctx.message.author.mention, base.name, base.posToStr()))
		except ValueError:
			await bot.say('Invalid syntax, try again (?addbase [name] [x coord] [z coord])')
			
	else :
		await bot.say('Allows you to add your base location to the database. '
			'Syntax: ?addbase [Base Name] [X Coordinate] [Z Coordinate]')

@bot.command(pass_context=True)			
async def findbase(ctx, * args):
	'''Allows you to find a base in the database.'''
	base = session.query(Location).filter_by(name=args[0]).first()
	if (base is not None) :
		await bot.say('{}, {} is located at {}.'.format(ctx.message.author.mention, base.name, base.posToStr()))
	else :
		await bot.say('{}, {} is not in the database'.format(ctx.message.author.mention, args[0]))
				
#Bot Startup ******************************************************************	
try :
	file = open('token.dat','r')
	TOKEN = file.read()	
except FileNotFoundError:
	print('token.dat not found.')
except IOError:
	print('Error reading token.dat')

bot.run(TOKEN)