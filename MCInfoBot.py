import discord
import enum
from discord.ext import commands
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, ForeignKey, Enum
from sqlalchemy.orm import sessionmaker

TOKEN = ''
command_prefix = '?'
description = '''Geoffrey is an inside joke none of you will understand, at 
least he knows where your bases are.

Please respect Geoffrey, the bot is very sensitive.
'''
engine = create_engine('sqlite:///:memory:', echo=True)
SQL_Base = declarative_base()		

bot = commands.Bot(command_prefix=command_prefix , description=description)

class TunnelDirection(enum.Enum) :
	North = 'green'
	East = 'blue'
	South = 'red'
	West = 'yellow'

class Player(SQL_Base):
	__tablename__ = 'Players'
	
	id = Column(Integer, primary_key=True)
	in_game_name = Column(String)
	
	def __init__(self,name) :
		self.in_game_name = name
	

class Location(SQL_Base):
	__tablename__ = 'Locations'
	
	id = Column(Integer, primary_key=True)
	name = Column(String)	
	x = Column(Integer)
	y = Column(Integer)
	z = Column(Integer)
	tunnelNumber = Column(Integer)
	direction = Column(Enum(TunnelDirection))
	owner = Column(String, ForeignKey('Players.in_game_name'))
	
	def __init__(self,args,owner) :
		self.name = args[0]
		self.x = int(args[1])
		self.y = int(args[2])
		self.z = int(args[3])
		self.owner = owner
		
		if (len(args) >= 5) :
			self.tunnelNumber =  int(args[5])
			self.direction =  strToTunnelDirection(args[4])

	def  posToStr(self) :
		return '(x= {}, y= {}, z= {})'.format(self.x, self.y, self.z)
	def netherTunnelAddrToStr(self) :
		return '{} {}'.format(self.direction.value.title(), self.tunnelNumber)
	
	def __str__(self):
		if (self.direction is not None) :
			return "Name: {}, Position: {}, Tunnel: {}".format(self.name,self.posToStr(),self.netherTunnelAddrToStr())
		else :
			return "Name: {}, Position: {}".format(self.name,self.posToStr())
		
SQL_Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()
		
def strToTunnelDirection(str) :
	str = str.lower()
	if (str == TunnelDirection.North.value) :
		return TunnelDirection.North
	elif (str == TunnelDirection.East.value) :
		return TunnelDirection.East
	elif (str == TunnelDirection.South.value):
		return TunnelDirection.South
	elif (str == TunnelDirection.West.value):
		return TunnelDirection.West
	else:
		raise ValueError
			
#Bot Commands ******************************************************************		
@bot.event
async def on_ready():
	print('GeoffreyBot')
	print('Username: ' + bot.user.name)
	print('ID: ' + bot.user.id)

@bot.command()
async def test():
	'''Check if the bot is alive.'''
	await bot.say('I\'m here you ding dong')

@bot.command(pass_context=True)
async def addbase(ctx, * args):
	'''Add your base to the database.
		?addbase [Base Name] [X Coordinate] [Y Coordinate] [Z Coordinate]
	'''
	if (len(args) == 4) :
		try:
			owner = Player(str(ctx.message.author.nick))
			base = Location(args,owner.in_game_name)
			
			session.add(owner)
			session.add(base)
			
			await bot.say('{}, your base named {} located at {} has been added'
				' to the database.'.format(ctx.message.author.mention, base.name, base.posToStr()))
		except ValueError:
			await bot.say('Invalid syntax, try again (?addbase [name] [x coord] [z coord])')
	elif(len(args) == 6) :
		try:
			owner = Player(str(ctx.message.author.nick))
			base = Location(args,owner.in_game_name)
			
			session.add(owner)
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
	'''Allows you to find a base in the database.
		?findbase [Player name]
	'''
	if (len(args) > 0) :
		
		baseList = session.query(Location).filter_by(owner=args[0]).all()
		
		if (baseList is not None) :
			await bot.say('{}, {} has {} base(s):'.format(ctx.message.author.mention,args[0], len(baseList)))
			for base in baseList:
				await bot.say(base)
		else :
			await bot.say('{}, {} is not in the database'.format(ctx.message.author.mention, args[0]))
	else :
		await bot.say('Allows you to add your base location to the database. '
			'Syntax: ?findbase [Base Name] ')
	
#Bot Startup ******************************************************************	
try :
	file = open('token.dat','r')
	TOKEN = file.read()	
except FileNotFoundError:
	print('token.dat not found.')
except IOError:
	print('Error reading token.dat')

bot.run(TOKEN)