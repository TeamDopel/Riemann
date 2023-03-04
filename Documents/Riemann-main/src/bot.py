import discord
import os
import datetime
from typing import List, Dict
from emoji import emojize
from discord import app_commands
from itertools import chain
from uuid import UUID, uuid4
from summarize import generate_summary, query_summary
from translate import translate

### LOADS ENV VARS ###
from dotenv import load_dotenv

load_dotenv()

summaries: Dict[UUID, List[discord.Message]] = {}

intents = discord.Intents(messages=True, message_content=True)
client = discord.Client(intents=intents)
tree = app_commands.CommandTree(client)

async def last_n_messages(channel: discord.TextChannel, n: int = 20) -> List[discord.Message]:
	"""
 	Gets last n messages in chronological order.
	"""
	return list(reversed([message async for message in channel.history(limit=n) if message.author != client.user and message.content]))

def format_attachment(attachment: discord.Attachment) -> str:
	if attachment.description:
		return f"{attachment.filename} ({attachment.description})"
	else:
		return attachment.filename

def format_message(message: discord.Message) -> str:
	"""
 	SuperSonicDiscord1#4741 at {time}: Hello, world! <attachments: hello.png (man waving)>
	"""

	message_to_send = f"{message.author.display_name} at {message.created_at}: {emojize(message.clean_content, language='alias')}"

	if message.attachments:
		message_to_send += f" <attachments: {', '.join(format_attachment(attachment) for attachment in message.attachments)}>"
	
	return message_to_send

async def get_first_summarzation_id(channel: discord.abc.Messageable) -> UUID:
	async for message in channel.history():
		if message.author != client.user:
			continue
		print(message)
		print(message.created_at)
		for embed in message.embeds:
			for field in embed.fields:
				if field.name == "summarization_id":
					return UUID(field.value)

def run_discord_bot():
	# Change your token here
	TOKEN = os.getenv("DISCORD_BOT_TOKEN")
	print(TOKEN)
	@client.event
	async def on_ready():
		await tree.sync()
		print(f'{client.user} is now running!')

	@client.event
	async def on_message(message: discord.Message):
		channel = message.channel
		if message.author != client.user and isinstance(channel, discord.channel.DMChannel):
			query = message.content

			summarization_id = await get_first_summarzation_id(channel)
			
			messages = summaries[summarization_id]
			formatted_messages = { message.id: format_message(message) for message in messages }
			await message.channel.send(query_summary(query, formatted_messages))


	@tree.command(name = "tldr", description = "Summarize and query an ongoing conversation.")
	async def summarizeCommand(
		interaction: discord.Interaction,
		number_of_messages: int = 50
	):
		async def send_dm():
			messages = await last_n_messages(interaction.channel, n=number_of_messages)
			summarization_id = uuid4()
			summaries[summarization_id] = messages
	
			users = {message.author for message in messages}
			embed_urls = set(embed.url for embed in chain.from_iterable(message.embeds for message in messages) if embed.url)
			oldest_message, newest_message = messages[0].created_at, messages[-1].created_at
			duration = newest_message - oldest_message
			formatted_messages = '\n'.join(format_message(message) for message in messages)

			embed = (
				discord.Embed(
					title=f"Here's what I got from the last {len(messages)} messages",
					description=generate_summary(formatted_messages),
				)
				.set_author(name=", ".join(user.display_name for user in users))
				.add_field(name="Start", value=oldest_message.strftime("%c"))
				.add_field(name="End", value=newest_message.strftime("%c"))
				.set_footer(text="Don't understand something? Your friend started speaking Shakespearean English? Ask a question and I will give you some more information!")
				.add_field(name="summarization_id", value=str(summarization_id), inline=False)
			)

			await interaction.user.send(embed=embed)

		await interaction.response.send_message("Check DMs for a summary! ;)", ephemeral=True)
		await send_dm()


	@tree.command(name = "translate", description = "Translate some text! Choose starting language and result language")
	async def translateCommand(interaction: discord.Interaction, source_language: str, translation_language: str, text:str):
		translation = translate(source_language, translation_language, text)
		if 'errors' in translation.keys(): 
			await interaction.response.send_message(
				translation['errors']['message'][0], 
				ephemeral=True
				)
		else: 
			await interaction.response.send_message(
				translation[list(translation.keys())[0]], 
				ephemeral=True
				)

	@tree.command(name = "translate-chat", description = "Translate some text! Choose starting language and result language")
	async def translateChat(
		interaction: discord.Interaction, 
		source_language: str, 
		translation_language: str,
		number_of_messages: int = 50):
		
		error_found = False

		if len(source_language) != 2:
			await interaction.response.send_message('Source Language Invalid')
			return ''
		if len(translation_language) != 2:
			await interaction.response.send_message('Translation Language Invalid')
			return ''
		async def send_dm():
			messages = await last_n_messages(interaction.channel, n=number_of_messages)

			def formatTime(time_str):
				try:
					dt = datetime.datetime.strptime(time_str[:-6], '%Y-%m-%d %H:%M:%S.%f')
					return f'{dt.strftime("%b %d %Y at %I:%M%p")}'
				except:
					return 'Error Getting Time'
			
			for message in messages:
				user = message.author
				translation = translate(source_language, translation_language, emojize(message.clean_content, language='alias'))
				if 'errors' in translation.keys(): 
					await interaction.response.send_message(
						translation['errors']['message'][0], 
						ephemeral=True
						)
					error_found = True
					break
				elif not error_found:
					embed = (
						discord.Embed(
							description=translation['translation']
						)
						.set_author(name=user.display_name)
						.set_footer(text=f'{formatTime(str(message.created_at))}')
					)

					await interaction.user.send(embed=embed)
		
		await send_dm()
		# switch to an if statement for speed
		try:
			await interaction.response.send_message(translate(source_language, translation_language, "Check DMs for a translation! ;)")['translation'], ephemeral=True)
		except KeyError:
			pass
	# Remember to run your bot with your personal TOKEN
	client.run(TOKEN)
