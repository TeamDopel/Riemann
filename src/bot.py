from utils import *

from discord.ext import commands

summaries: Dict[UUID, List[discord.Message]] = {}

intents = discord.Intents(messages=True, message_content=True)
client = discord.Client(intents=intents)
bot = commands.Bot(command_prefix='!', intents=intents, client=client)
tree = app_commands.CommandTree(client)

def run_discord_bot():
	# Change your token here
	TOKEN = os.getenv("DISCORD_BOT_TOKEN")
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
		print(f'src-lang: {source_language} \n trans-lang:{translation_language} \n text: {text}')
		embed = (
			discord.Embed(
				description=translate(source_language, translation_language, text)['translation']
			)
		)
		await interaction.response.send_message(translate(source_language, translation_language, "Check DMs for a translation!")['translation'], ephemeral=True)
		await interaction.user.send(embed=embed)

	@tree.command(name = "translate-chat", description = "Translate some text! Choose starting language and result language")
	async def translateChat(
		interaction: discord.Interaction, 
		source_language: str, 
		translation_language: str,
		number_of_messages: int = 50):
		if len(source_language) != 2:
			await interaction.response.send_message('Source Language Invalid')
			return ''
		if len(translation_language) != 2:
			await interaction.response.send_message('Translation Language Invalid')
			return ''
		async def send_dm():
			messages = await last_n_messages(interaction.channel, n=number_of_messages)
	
			#users = {message.author for message in messages}
			#embed_urls = set(embed.url for embed in chain.from_iterable(message.embeds for message in messages) if embed.url)
			#oldest_message, newest_message = messages[0].created_at, messages[-1].created_at
			#duration = newest_message - oldest_message
			def formatTime(time_str):
				dt = datetime.datetime.strptime(time_str[:-6], '%Y-%m-%d %H:%M:%S.%f')
				return f'{dt.strftime("%b %d %Y at %I:%M%p")}'
			
			for message in messages:
				user = message.author
				embed = (
					discord.Embed(
						description=translate(source_language, translation_language, emojize(message.clean_content, language='alias'))['translation']
					)
					.set_author(name=user.display_name)
					.set_footer(text=f'{formatTime(str(message.created_at))}')
				)

				await interaction.user.send(embed=embed)

		await interaction.response.send_message("Check DMs for a summary! ;)", ephemeral=True)
		await send_dm()
	# Remember to run your bot with your personal TOKEN
	client.run(TOKEN)
