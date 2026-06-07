import asyncio
from loguru import logger
from config import Channels, LogsColor
from config.config import TOKEN
from logs import Logs
from main import bot, load_cogs


@bot.event
async def on_ready():
    logger.info(f"{bot.user} has logged in, starting command synchronization...")

    try:
        await bot.tree.sync()
        log = Logs(
            category=Channels.LOGS_TECHNICAL,
            message="Commands have been successfully synchronized",
            color=LogsColor.GREEN,
        )
        await log.send_log(bot)
    except Exception as e:
        bot.sync_error = e
        log = Logs(
            category=Channels.LOGS_TECHNICAL,
            message="An error occurred while synchronizing commands.",
            color=LogsColor.RED,
        )
        await log.send_log(bot)
    finally:
        logger.info("Closing the synchronization bot...")
        await bot.close()


async def run_sync():
    bot.sync_error = None
    token = TOKEN if isinstance(TOKEN, str) else None
    if token is None or not token.strip():
        raise RuntimeError("TOKEN is not set. Configure config.config.TOKEN before starting" " the bot.")

    async with bot:
        logger.info("Loading cogs before synchronization...")
        await load_cogs(bot)
        await bot.start(token)
        if bot.sync_error is not None:
            raise RuntimeError("Command synchronization failed:" f" {str(bot.sync_error)}") from bot.sync_error


if __name__ == "__main__":
    asyncio.run(run_sync())
