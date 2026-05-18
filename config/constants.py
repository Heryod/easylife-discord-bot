from enum import IntEnum
from discord import Guild

class Users(IntEnum):
  HERYOD = 914860500364439572
  ADEX = 391410755506929665

class Roles(IntEnum):
  ADMIN = 1112837003185225848
  MEMBER = 1349467306144825415
  BOT = 1126619740316647484

class Channels(IntEnum):
  #? Logs 
  LOGS_GENERAL = 1505946757731979394
  LOGS_TICKET = 1505946774584692866
  LOGS_SECURITY = 1505946792687177758

  MAIN = 1505610621910257754
  RANK_COLLECT = 1505947969235718164

class Categories(IntEnum):
  TICKETS = 1505947481144430803

class CommandRoles(IntEnum):
  PREMIUM = 1212071055888351232
  LEAKS_PING = 1505975735943430285
  EVENTS_PING = 1505975692691640502

class Permissions():
  @staticmethod
  def is_high_admin(user_id: int) -> bool:
    return user_id in {Users.HERYOD, Users.ADEX}
  
  @staticmethod 
  async def is_staff(guild: Guild | None, user_id: int) -> bool:
    if guild is None:
      return False
    member = await guild.fetch_member(user_id)

    if Permissions.is_high_admin(user_id):
      return True

    role_ids = [role.id for role in member.roles]
    
    return Roles.ADMIN in role_ids