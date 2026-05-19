import discord
from loguru import logger
import sys


async def add_role(member: discord.User | discord.Member, role: discord.Role) -> bool:
    """
    Adds a role to a user
    """
    try:
        if not isinstance(member, discord.Member):
            logger.error(f"User {member} is not a guild member")
            return False

        if role in member.roles:
            logger.warning(f"User {member} already has role {role.name}")
            return False

        await member.add_roles(role)
        logger.info(f"Added role '{role.name}' to user {member}")
        return True

    except discord.Forbidden:
        logger.error(f"Insufficient permissions to add role {role.name} to user {member}")
        return False
    except Exception as e:
        logger.error(f"Error while adding role {role.name}: {e}")
        return False


async def remove_role(member: discord.User | discord.Member, role: discord.Role) -> bool:
    """
    Removes a role from a user
    """
    try:
        if not isinstance(member, discord.Member):
            logger.error(f"User {member} is not a guild member")
            return False

        if role not in member.roles:
            logger.warning(f"User {member} doesn't have role {role.name}")
            return False

        await member.remove_roles(role)
        logger.info(f"Removed role '{role.name}' from user {member}")
        return True

    except discord.Forbidden:
        logger.error(f"Insufficient permissions to remove role {role.name} from user {member}")
        return False
    except Exception as e:
        logger.error(f"Error while removing role {role.name}: {e}")
        return False


async def toggle_role(member: discord.User | discord.Member, role: discord.Role) -> bool:
    """
    Toggles a role for a user - adds if they don't have it, removes if they do
    """
    try:
        if not isinstance(member, discord.Member):
            logger.error(f"User {member} is not a guild member")
            return False

        if role in member.roles:
            return await remove_role(member, role)
        else:
            return await add_role(member, role)

    except Exception as e:
        logger.error(f"Error while toggling role {role.name}: {e}")
        return False
