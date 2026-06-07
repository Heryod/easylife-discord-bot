import asyncio
from pathlib import Path
import discord
from discord.ext import commands
from loguru import logger

from cogs import handle_expired_roles
from config import Channels, LogsColor
from config.config import TOKEN
from logs import Logs
from utils import get_status, load_cogs


class CustomBot(commands.Bot):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sync_error: Exception | None = None


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True
bot = CustomBot(command_prefix="/", intents=intents)


async def status_loop():
    await bot.wait_until_ready()
    last_status = None

    while not bot.is_closed():
        try:
            loop = asyncio.get_event_loop()
            current_status = await loop.run_in_executor(None, get_status)

            if current_status != last_status:
                await bot.change_presence(activity=discord.Game(name=current_status))
                logger.info(f"Status changed: {last_status!r} → {current_status!r}")
                last_status = current_status

        except Exception as e:
            logger.error(f"status_loop error: {e}")

        await asyncio.sleep(60)


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has logged in")
    await handle_expired_roles(bot)


async def main():
    token = TOKEN if isinstance(TOKEN, str) else None
    if token is None or not token.strip():
        raise RuntimeError("TOKEN is not set")

    async with bot:
        await load_cogs(bot)
        bot.loop.create_task(status_loop())
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
