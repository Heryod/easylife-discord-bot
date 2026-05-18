import discord
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select
from config import Permissions
from config.constants import CommandRoles
from utils import create_role_panel_embed
from utils.helpers import toggle_role


class RoleSelect(Select):
  """Persistent select menu for role selection"""
  def __init__(self, options, cog):
    super().__init__(
      placeholder="Wybierz powiadomienia",
      options=options,
      custom_id="role_select" 
    )
    self.cog = cog
  
  async def callback(self, interaction: discord.Interaction):
    """handler for user selection - adds or removes the selected role"""
    if not interaction.guild:
      await interaction.response.defer()
      return
    
    selected_value = self.values[0]
    member = interaction.user
    
    role_mapping = {
      "events_ping": CommandRoles.EVENTS_PING,
      "leaks_ping": CommandRoles.LEAKS_PING
    }
    
    role_id = role_mapping.get(selected_value)
    if not role_id:
      await interaction.response.defer()
      return
    
    role = interaction.guild.get_role(role_id)
    
    if not role:
      await interaction.response.defer()
      return
    
    await toggle_role(member, role)
    await interaction.response.send_message(f"Rola {role.name} została zaktualizowana.", ephemeral=True)


class RolePersistentView(View):
  """Persistent view for the role selection panel"""
  def __init__(self, options, cog):
    super().__init__(timeout=None)
    self.add_item(RoleSelect(options, cog))


class RolesCog(commands.Cog):
  def __init__(self, bot: commands.Bot):
    self.bot = bot
    embed, self.role_options = create_role_panel_embed()
    self.bot.add_view(RolePersistentView(self.role_options, self))

  @app_commands.command(name="role-panel", description="Wysyła panel wyboru ról")
  async def rolePanel(self, interaction: discord.Interaction):
    """Slash command that sends the role selection panel"""
    
    if not Permissions.is_high_admin(interaction.user.id):
      await interaction.response.send_message("Nie masz uprawnień do użycia tej komendy.", ephemeral=True)
      return
    
    embed, options = create_role_panel_embed()
    view = RolePersistentView(options, self)
    await interaction.response.send_message(embed=embed, view=view)


async def setup(bot: commands.Bot):
  """Function needed to load the cog."""
  await bot.add_cog(RolesCog(bot))