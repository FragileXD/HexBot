import os
import io
import datetime
import json
from aiohttp import ClientSession
import ksoftapi

import discord
from discord.ext import commands

from utils import canvas

bot = commands.Bot(command_prefix=commands.when_mentioned_or("~"),
					description='Relatively simply awesome bot.',
					case_insensitive=True,
					intents=discord.Intents.all())

bot.remove_command('help')

bot.uptime = datetime.datetime.now()
bot.messages_in = bot.messages_out = 0
bot.region = 'Mumbai, IN'

@bot.event
async def on_ready():
	print('Logged in as {0} ({0.id})'.format(bot.user))
	bot.kclient = ksoftapi.Client(os.environ['KSoft_Token'])
	bot.client = ClientSession()

	# Load Modules
	modules = ['misc', 'games', 'debug', 'media', 'music']
	try:
		for module in modules:
			bot.load_extension('cogs.' + module)
			print('Loaded: ' + module)
	except Exception as e:
		print(f'Error loading {module}: {e}')

	print('Bot.....Activated')
	await bot.change_presence(status=discord.Status.online, activity=discord.Game(name="Nothing"))

@bot.event
async def on_message(message):
	# Sent message
	if message.author.id == bot.user.id:
		if hasattr(bot, 'messages_out'):
			bot.messages_out += 1
	# Received message (Count only commands messages)
	elif message.content.startswith('~'):
		if hasattr(bot, 'messages_in'):
			bot.messages_in += 1

	await bot.process_commands(message)

@bot.event
async def on_guild_join(guild):
	for channel in guild.text_channels:
		if channel.permissions_for(guild.me).send_messages:
			await channel.send('Hey there! Thank you for adding me!\nMy prefix is `~`\nStart by typing `~help`')
			break

@bot.event
async def on_member_join(member):
	sys_channel = member.guild.system_channel
	if sys_channel:
		data = await canvas.member_banner('Welcome', str(member), str(member.avatar_url_as(format='png', size=256)))
		with io.BytesIO() as img:
			data.save(img, 'PNG')
			img.seek(0)
			try:
				await sys_channel.send(content=member.mention, file=discord.File(fp=img, filename='welcome.png'))
			except discord.Forbidden:
				pass

@bot.event
async def on_member_remove(member):
	sys_channel = member.guild.system_channel
	if sys_channel:
		data = await canvas.member_banner('Bye Bye', str(member), str(member.avatar_url_as(format='png', size=256)))
		with io.BytesIO() as img:
			data.save(img, 'PNG')
			img.seek(0)
			try:
				await sys_channel.send(file=discord.File(fp=img, filename='leave.png'))
			except discord.Forbidden:
				pass

@bot.command(name='help', aliases=['h'])
async def help(ctx, arg: str=''):
	"""Display help"""
	embed = discord.Embed(title="Relatively simply awesome bot.", colour=discord.Colour(0x7f20a0))

	avatar_url = str(bot.user.avatar_url)
	embed.set_thumbnail(url=avatar_url)
	embed.set_author(name="HexBot Help", url="https://discord.com/oauth2/authorize?client_id=747461870629290035&scope=bot&permissions=57344", icon_url=avatar_url)
	embed.set_footer(text="HexBot by [Prototype]#7731✨")

	if arg.strip().lower() == '-a':
		# Full version
		embed.description = 'My prefix is `~`'
		with open('help.json', 'r') as help_file:
			data = json.load(help_file)
		data = data['full']
		for key in data:
			value = '\n'.join(x for x in data[key])
			embed.add_field(name=key, value=f"```{value}```", inline=False)
	else:
		# Short version
		embed.description = 'My prefix is `~`\nType `~help -a` for detailed help.'
		with open('help.json', 'r') as help_file:
			data = json.load(help_file)
		data = data['short']
		for key in data:
			embed.add_field(name=key, value=data[key])
	try:
		await ctx.send(embed=embed)
	except Exception:
		await ctx.send("I don't have permission to send embeds here :disappointed_relieved:")


# All good ready to start!
print('Starting Bot...')
bot.run(os.environ['BOT_Token'])
