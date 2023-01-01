import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
import json
import os

from music import Music

configPath = os.getcwd() + "/config.json"

if os.path.exists(configPath):

    with open("./config.json") as f:
        configData = json.load(f)
else:
    configTemplate = {"Token": "", "Prefix": "-"}

    with open(configPath, "w+") as f:
        json.dump(configTemplate, f)

token = configData["Token"]
prefix = configData["Prefix"]

intents = discord.Intents.all()
chatot = commands.Bot(command_prefix=prefix, intents=intents)

menu = DefaultMenu(active_time=45)
chatot.help_command = PrettyHelp(navigation=menu, color=discord.Color.lighter_gray(), show_index=False)


@chatot.event
async def on_ready():
    print(f"{chatot.user} is running!")
    await chatot.add_cog(Music(chatot))
    await chatot.tree.sync()


@chatot.tree.command(name="slash")
async def slash(interaction: discord.Interaction):
    await interaction.response.send_message("You must have had a bad dream or something!")


chatot.run(token)
