import discord
from discord.ext import commands
import asyncio
from pathlib import Path
from config.config import TOKEN
from loguru import logger

intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = commands.Bot(command_prefix="/", intents=intents)

@bot.event
async def on_ready():
    logger.info(f'{bot.user} has logged in')
    
    await bot.tree.sync()
    logger.info('commands synced')

async def load_cogs():
    """Loads all cogs from the cogs directory."""

    cogs_path = Path('cogs')
    for cog_file in cogs_path.glob('*.py'):
        if cog_file.name.startswith('_'):
            continue
        cog_name = f'cogs.{cog_file.stem}'
        try:
            await bot.load_extension(cog_name)
            logger.info(f'loaded cog: {cog_name}')
        except Exception as e:
            logger.error(f'failed to load {cog_name}: {e}')

async def main():
    async with bot:
        await load_cogs()
        await bot.start(str(TOKEN))

if __name__ == '__main__':
    asyncio.run(main())
