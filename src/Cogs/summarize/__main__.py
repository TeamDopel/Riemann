### START: FOLDER SETUP ###
import os, sys

sys.path.append(
    os.path.dirname(
        os.path.dirname(
            os.path.dirname(
                os.path.abspath(__file__)
            )
        )    
    )
)

from utils import *
### END: FOLDER SETUP ###

from summarize import generate_summary, query_summary
from discord.ext import commands
class TestCog(commands.Cog):
  def __init__(self, bot: commands.Bot) -> None:
    self.bot = bot
  # Above, we declare a command Group, in discord terms this is a parent command
  # We define it within the class scope (not an instance scope) so we can use it as a decorator.
  # This does have namespace caveats but i don't believe they're worth outlining in our needs.

  @commands.command(name="top-command")
  async def my_top_command(self, interaction: discord.Interaction) -> None:
    """ /top-command """
    await interaction.response.send_message("Hello from top level command!", ephemeral=True)
def setup(bot):
    bot.add_cog(TestCog(bot))