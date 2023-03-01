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

import discord
from discord import app_commands
from discord.ext import commands

### LOADS ENV VARS ###
from dotenv import load_dotenv

load_dotenv()

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

def test():
	print('hello')