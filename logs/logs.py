import discord
from config import Channels, LogsColor
from datetime import datetime
from loguru import logger


async def log_error(error_message: str, bot: discord.Client):
    """
    Logs an error message to the console and updates the log message with the error details.
    """
    logger.error(error_message)
    logs = Logs(
        category=Channels.LOGS_TECHNICAL,
        message="An error occurred while sending the log message.",
        color=LogsColor.RED,
    )

    await logs.send_log(bot)


class Logs:
    """
    Class for creating and sending log messages to specific channels with appropriate formatting and colors.
    """

    def __init__(self, category: Channels, message: str, color: LogsColor):
        self.category = category
        self.message = message
        self.color = color.value
        self.channel_id = category.value

    def _generate_embed(self, message: str | None = None) -> discord.Embed:
        """
        Generates a Discord embed object based on the logs category, message, color, and timestamp.
        """
        if not message:
            message = self.message

        embed = discord.Embed(
            title=f"Logs - {self.category.name.replace('_', ' ').title()}",
            description=message,
            colour=self.color,
            timestamp=datetime.now(),
        )

        return embed

    def _send_console_log(self):
        """
        Logs the message to the console with appropriate formatting based on the log category.
        """
        if self.category == Channels.LOGS_TECHNICAL and self.color == LogsColor.RED.value:
            logger.error(self.message)
        elif getattr(LogsColor, "YELLOW", None) and self.color == LogsColor.YELLOW.value:
            logger.warning(self.message)
        else:
            logger.info(self.message)

    async def send_log(self, bot: discord.Client):
        """
        Sends the log message to the appropriate channel based on the category.
        """
        log_embed = self._generate_embed()
        channel = bot.get_channel(self.channel_id)
        if channel and isinstance(channel, discord.abc.Messageable):
            await channel.send(embed=log_embed)
            self._send_console_log()
        else:
            await log_error(
                f"Failed to send log message to channel ID {self.channel_id} - channel not found or not messageable",
                bot,
            )
