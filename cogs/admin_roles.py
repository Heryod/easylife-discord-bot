import discord
from typing import Optional
from datetime import datetime, timedelta
from discord.ext import commands
from discord import app_commands
from config import Permissions, CommandRoles, Channels, LogsColor
from config.config import GUILD_ID
from utils.helpers import add_role, remove_role
from utils.role_file_handler import remove_expired_roles, save_role, remove_role as remove_role_from_file, get_role, get_user_roles
from logs import Logs
from loguru import logger
import re


class AdminRoles(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

    @app_commands.command(
        name="rola",
        description="Nadaj rolę użytkownikowi",
    )
    @app_commands.describe(
        user="Użytkownik któremu chcesz nadać rolę",
        role="Rola do nadania",
        time="Opcjonalnie: czas wygasania (np. 7d, 24h, 30m)",
    )
    async def grant_role(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        role: discord.Role,
        time: Optional[str] = None,
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Nie można użyć tej komendy tutaj.", ephemeral=True)
            return

        if not await Permissions.is_staff(guild, interaction.user.id):
            await interaction.response.send_message("Nie masz uprawnień do korzystania z tej komendy.", ephemeral=True)
            return

        allowed_ids = {r.value for r in CommandRoles}
        if role.id not in allowed_ids:
            available_roles = ", ".join([r.name for r in CommandRoles])
            await interaction.response.send_message(
                f"Tej roli nie można nadać tą komendą. Dostępne role: {available_roles}",
                ephemeral=True,
            )
            return

        role_name = next(r.name for r in CommandRoles if r.value == role.id)

        member = guild.get_member(user.id)
        if not member:
            try:
                member = await guild.fetch_member(user.id)
            except discord.HTTPException:
                await interaction.response.send_message(
                    f"Nie znaleziono użytkownika {user} na serwerze.",
                    ephemeral=True,
                )
                return

        if get_role(user.id, role.id):
            await interaction.response.send_message(
                f"Użytkownik {user.mention} już posiada rolę **{role_name}**.",
                ephemeral=True,
            )
            return

        expiration_time = None
        if time:
            expiration_time = self._parse_time(time)
            if not expiration_time:
                await interaction.response.send_message(
                    "Nieprawidłowy format czasu. Użyj: 7d, 24h, 30m, itp.",
                    ephemeral=True,
                )
                return

        if not await add_role(member, role):
            await interaction.response.send_message(
                f"Nie udało się nadać roli **{role_name}** użytkownikowi {user.mention}.",
                ephemeral=True,
            )
            return

        save_role(
            user_id=user.id,
            role_id=role.id,
            role_name=role_name,
            granted_by=interaction.user.id,
            granted_by_name=interaction.user.name,
            expiration_time=expiration_time,
        )

        expiration_info = ""
        if expiration_time:
            dt = datetime.fromisoformat(expiration_time)
            expiration_info = f"\n**Do kiedy:** {dt.strftime('%d.%m.%Y %H:%M')}"

        log_message = (
            f"Rola **{role_name}** nadana\n"
            f"**Komu:** {user.mention}\n"
            f"**Przez:** {interaction.user.mention}\n"
            f"**Data nadania:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            f"{expiration_info}"
        )

        log = Logs(
            category=Channels.LOGS_ROLE,
            message=log_message,
            color=LogsColor.GREEN,
        )
        await log.send_log(self.bot)

        response_msg = f"Rola **{role_name}** została nadana użytkownikowi {user.mention}"
        if expiration_time:
            response_msg += f"\nWygaśnie: {expiration_time}"

        await interaction.response.send_message(response_msg, ephemeral=True)

    @app_commands.command(
        name="rola-usun",
        description="Usuń rolę użytkownikowi",
    )
    @app_commands.describe(
        user="Użytkownik któremu chcesz usunąć rolę",
        role="Rola do usunięcia",
    )
    async def remove_role_cmd(
        self,
        interaction: discord.Interaction,
        user: discord.User,
        role: discord.Role,
    ):
        guild = interaction.guild
        if not guild:
            await interaction.response.send_message("Nie można użyć tej komendy tutaj.", ephemeral=True)
            return

        if not await Permissions.is_staff(guild, interaction.user.id):
            await interaction.response.send_message("Nie masz uprawnień do korzystania z tej komendy.", ephemeral=True)
            return

        allowed_ids = {r.value for r in CommandRoles}
        if role.id not in allowed_ids:
            available_roles = ", ".join([r.name for r in CommandRoles])
            await interaction.response.send_message(
                f"Tej roli nie można usunąć tą komendą. Dostępne role: {available_roles}",
                ephemeral=True,
            )
            return

        role_name = next(r.name for r in CommandRoles if r.value == role.id)

        member = guild.get_member(user.id)
        if not member:
            try:
                member = await guild.fetch_member(user.id)
            except discord.HTTPException:
                await interaction.response.send_message(
                    f"Nie znaleziono użytkownika {user} na serwerze.",
                    ephemeral=True,
                )
                return

        if not get_role(user.id, role.id):
            await interaction.response.send_message(
                f"Użytkownik {user.mention} nie posiada roli **{role_name}**.",
                ephemeral=True,
            )
            return

        if not await remove_role(member, role):
            await interaction.response.send_message(
                f"Nie udało się usunąć roli **{role_name}** użytkownikowi {user.mention}.",
                ephemeral=True,
            )
            return

        remove_role_from_file(user.id, role.id)

        log_message = (
            f"Rola **{role_name}** usunięta\n"
            f"**Komu:** {user.mention}\n"
            f"**Przez:** {interaction.user.mention}\n"
            f"**Data usunięcia:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )

        log = Logs(
            category=Channels.LOGS_ROLE,
            message=log_message,
            color=LogsColor.YELLOW,
        )
        await log.send_log(self.bot)

        await interaction.response.send_message(
            f"Rola **{role_name}** została usunięta użytkownikowi {user.mention}",
            ephemeral=True,
        )

    def _parse_time(self, time_str: str) -> Optional[str]:
        try:
            time_str = time_str.lower().strip()

            match = re.match(r"^(\d+)([dhm])$", time_str)
            if not match:
                return None

            amount = int(match.group(1))
            unit = match.group(2)

            now = datetime.now()
            if unit == "d":
                expiration = now + timedelta(days=amount)
            elif unit == "h":
                expiration = now + timedelta(hours=amount)
            elif unit == "m":
                expiration = now + timedelta(minutes=amount)
            else:
                return None

            return expiration.isoformat()

        except Exception as e:
            logger.error(f"Error parsing time string '{time_str}': {e}")
            return None


async def handle_expired_roles(bot):
    """Removes all expired roles from users and logs the action."""
    try:
        expired_roles = remove_expired_roles()

        if not expired_roles:
            logger.info("No expired roles found")
            return

        guild = bot.get_guild(GUILD_ID)
        if not guild:
            logger.warning(f"Guild {GUILD_ID} not found for expired role cleanup")
            return

        for expired_role in expired_roles:
            try:
                user_id = expired_role.get("user_id")
                role_id = expired_role.get("role_id")
                role_name = expired_role.get("role_name", "Unknown")

                if not isinstance(user_id, int) or not isinstance(role_id, int):
                    logger.warning(f"Invalid user_id or role_id for expired role: {expired_role}")
                    continue

                member = guild.get_member(user_id)
                if not member:
                    try:
                        member = await guild.fetch_member(user_id)
                    except discord.HTTPException:
                        logger.warning(f"Could not fetch member {user_id} for expired role removal")
                        continue

                discord_role = guild.get_role(role_id)
                if discord_role and discord_role in member.roles:
                    await member.remove_roles(discord_role)
                    logger.info(f"Removed expired role {role_name} from user {user_id}")

                    log_message = (
                        f"Rola **{role_name}** wygasła i została usunięta\n"
                        f"**Od:** <@{user_id}>\n"
                        f"**Data wygaśnięcia:** {expired_role.get('expires_at', 'Unknown')}"
                    )
                    log = Logs(
                        category=Channels.LOGS_ROLE,
                        message=log_message,
                        color=LogsColor.BLUE,
                    )
                    await log.send_log(bot)

            except Exception as e:
                logger.error(f"Error removing expired role {expired_role.get('role_id')}: {e}")

        logger.info(f"Removed {len(expired_roles)} expired roles")

    except Exception as e:
        logger.error(f"Error handling expired roles: {e}")


async def setup(bot: commands.Bot):
    await bot.add_cog(AdminRoles(bot))
