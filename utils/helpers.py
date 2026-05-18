import discord
from loguru import logger
import sys


logger.remove()
logger.add(
    sys.stdout,
    format="<green>{time:HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
    level="INFO"
)


async def add_role(member: discord.User | discord.Member, role: discord.Role) -> bool:
    """
    Adds a role to a user
    
    Args:
        member: User to whom the role will be added (must be Member in guild)
        role: role to add
        
    Returns:
        True if success, False if error or already has role
    """
    try:
        if not isinstance(member, discord.Member):
            logger.error(f"❌ User {member} is not a guild member")
            return False
            
        if role in member.roles:
            logger.warning(f"User {member} already has role {role.name}")
            return False
        
        await member.add_roles(role)
        logger.info(f"✅ Added role '{role.name}' to user {member}")
        return True
        
    except discord.Forbidden:
        logger.error(f"❌ Insufficient permissions to add role {role.name} to user {member}")
        return False
    except Exception as e:
        logger.error(f"❌ Error while adding role {role.name}: {e}")
        return False


async def remove_role(member: discord.User | discord.Member, role: discord.Role) -> bool:
    """
    Removes a role from a user
    
    Args:
        member: User from whom the role will be removed (must be Member in guild)
        role: Role to remove
        
    Returns:
        True if success, False if error or user doesn't have the role
    """
    try:
        if not isinstance(member, discord.Member):
            logger.error(f"❌ User {member} is not a guild member")
            return False
            
        if role not in member.roles:
            logger.warning(f"User {member} doesn't have role {role.name}")
            return False
        
        await member.remove_roles(role)
        logger.info(f"✅ Removed role '{role.name}' from user {member}")
        return True
        
    except discord.Forbidden:
        logger.error(f"❌ Insufficient permissions to remove role {role.name} from user {member}")
        return False
    except Exception as e:
        logger.error(f"❌ Error while removing role {role.name}: {e}")
        return False


async def toggle_role(member: discord.User | discord.Member, role: discord.Role) -> bool:
    """
    Toggles a role for a user - adds if they don't have it, removes if they do
    
    Args:
        member: User (must be Member in guild)
        role: Role to toggle
        
    Returns:
        True if success, False if error
    """
    try:
        if not isinstance(member, discord.Member):
            logger.error(f"❌ User {member} is not a guild member")
            return False
            
        if role in member.roles:
            return await remove_role(member, role)
        else:
            return await add_role(member, role)
            
    except Exception as e:
        logger.error(f"❌ Error while toggling role {role.name}: {e}")
        return False
        return False
