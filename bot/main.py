import discord
from bot.config import TOKEN 

intents = discord.Intents.default()
intents.message_content = True
bot = discord.Client(intents=intents)

@bot.event
async def on_ready():
    print(f'{bot.user} has logged in!')

bot.run(TOKEN)
