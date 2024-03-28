import discord
from discord.ext import commands
from pretty_help import DefaultMenu, PrettyHelp
import json
import os

from music import Music
from movesearch import search_moves, format_embed

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
    print(f"{chatot.user} is running!")


@chatot.command()
async def nms(ctx, *, pokemon_list):
    if not pokemon_list:
        await ctx.send("Please provide at least one Pokemon.")
        return

    pokemon_list = [pokemon.strip() for pokemon in pokemon_list.split(',')]
    results = await search_moves(pokemon_list)

    embed = await format_embed(results)

    await ctx.send(embed=embed)


@chatot.tree.command(name="test")
async def slash(interaction: discord.Interaction):
    await interaction.response.send_message("test")

chatot.run(token)
