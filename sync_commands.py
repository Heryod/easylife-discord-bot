import asyncio
from loguru import logger
from main import bot, load_cogs
from config.config import TOKEN
from logs import Logs
from config import Channels, LogsColor

sync_error = None


@bot.event
async def on_ready():
    global sync_error
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
        sync_error = e
        log = Logs(
            category=Channels.LOGS_TECHNICAL,
            message="An error occurred while synchronizing commands.",
            color=LogsColor.RED,
        )
        await log.send_log(bot)
        raise
    finally:
        logger.info("Closing the synchronization bot...")
        await bot.close()


async def run_sync():
    global sync_error
    sync_error = None
    token = TOKEN if isinstance(TOKEN, str) else None
    if token is None or not token.strip():
        raise RuntimeError("TOKEN is not set. Configure config.config.TOKEN before starting the bot.")

    async with bot:
        logger.info("Loading cogs before synchronization...")
        await load_cogs()
        await bot.start(token)
    if sync_error is not None:
        raise RuntimeError("Command synchronization failed.") from sync_error


if __name__ == "__main__":
    asyncio.run(run_sync())
