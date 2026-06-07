import asyncio
import discord
from discord.ext import commands, tasks
from loguru import logger
from cogs import handle_expired_roles
from config.config import TOKEN
from utils import get_status, load_cogs


class CustomBot(commands.Bot):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.sync_error: Exception | None = None
        self._last_status = None 

    async def setup_hook(self):
        await load_cogs(self)
        
        self.status_loop.start()

    @tasks.loop(seconds=60)
    async def status_loop(self):
        try:
            current_status = await asyncio.to_thread(get_status)

            if current_status != self._last_status:
                await self.change_presence(activity=discord.Game(name=current_status))
                logger.info(f"Status changed: {self._last_status!r} → {current_status!r}")
                self._last_status = current_status
        except Exception as e:
            logger.error(f"status_loop error: {e}")

    @status_loop.before_loop
    async def before_status_loop(self):
        await self.wait_until_ready()


intents = discord.Intents.default()
intents.message_content = True
intents.guilds = True
intents.members = True

bot = CustomBot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has logged in")
    await handle_expired_roles(bot)


async def main():
    token = TOKEN if isinstance(TOKEN, str) else None
    if token is None or not token.strip():
        raise RuntimeError("TOKEN is not set")

    async with bot:
        await bot.start(token)


if __name__ == "__main__":
    asyncio.run(main())
