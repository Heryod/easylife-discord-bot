import json
import os
from typing import Optional
import discord
from discord import app_commands
from discord.ext import commands
from loguru import logger
from config import Permissions

STATUS_FILE = "data/status.json"


def _write_status(value: str) -> None:
    os.makedirs(os.path.dirname(STATUS_FILE), exist_ok=True)
    with open(STATUS_FILE, "w") as f:
        json.dump({"status": value}, f, indent=4)


class Status(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="status",
        description="Ustaw status bota",
    )
    @app_commands.describe(
        tekst="Opcjonalnie: własny tekst statusu. Bez parametru - pokaże liczbę graczy online.",
    )
    async def set_status(
        self,
        interaction: discord.Interaction,
        tekst: Optional[str] = None,
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Nie można użyć tej komendy tutaj.", ephemeral=True)
            return

        if not Permissions.is_high_admin(interaction.user.id):
            await interaction.response.send_message("Nie masz uprawnień do korzystania z tej komendy.", ephemeral=True)
            return

        if tekst:
            new_status = tekst.strip()
            display = f"**{new_status}**"
        else:
            new_status = "players"
            display = "liczba graczy online"

        try:
            _write_status(new_status)
        except Exception as e:
            logger.error(f"Failed to write status file: {e}")
            await interaction.response.send_message("Nie udało się zapisać statusu.", ephemeral=True)
            return

        logger.info(f"Status set to '{new_status}' by {interaction.user}")

        await interaction.response.send_message(f"Status bota ustawiony na: {display}", ephemeral=True)


async def setup(bot: commands.Bot):
    await bot.add_cog(Status(bot))
