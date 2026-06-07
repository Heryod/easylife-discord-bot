import discord
from typing import Optional, Union, List
from datetime import datetime
from discord.ext import commands
from discord import app_commands
from discord.ui import View, Select, Button, Modal, TextInput
from config import Permissions, Roles, Users, Channels, Categories, LogsColor
from utils.ticket_embed import create_ticket_embed, create_doj_ticket_embed, create_welcome_embed, create_closed_embed, create_doj_welcome_embed
from utils.ticket_file_handler import save_ticket, delete_ticket, get_ticket, get_user_ticket_count
from logs import Logs


async def can_manage_ticket(guild: discord.Guild, user_id: int, ticket_category: Optional[str]) -> bool:
    if await Permissions.is_staff(guild, user_id):
        return True

    if ticket_category == "doj":
        member = guild.get_member(user_id)
        if not member:
            try:
                member = await guild.fetch_member(user_id)
            except discord.HTTPException:
                return False

        return any(r.id == Roles.DOJ for r in member.roles)

    return False


class ConfirmCloseView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Potwierdź zamknięcie", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="admin_closeticket")
    async def confirm_close(self, interaction: discord.Interaction, button: Button):
        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Nie można użyć tej komendy tutaj.", ephemeral=True)
            return

        ticket_data = get_ticket(interaction.channel.id)
        ticket_category = ticket_data.get("category") if ticket_data else None

        if not await can_manage_ticket(interaction.guild, interaction.user.id, ticket_category):
            await interaction.response.send_message("Nie masz uprawnień do potwierdzenia zamknięcia tego ticketu.", ephemeral=True)
            return

        try:
            if ticket_data:
                creator_id = ticket_data.get("creator_id")
                created_at = ticket_data.get("created_at")
                log = Logs(
                    category=Channels.LOGS_TICKET,
                    message=f"Ticket **ID**: {interaction.channel.id}\nZostał trwale usunięty przez: <@{interaction.user.id}>\nAutor ticketu: <@{creator_id}>\nUtworzono: {created_at}",
                    color=LogsColor.RED,
                )
                await log.send_log(interaction.client)

            delete_ticket(interaction.channel.id)
            await interaction.channel.delete(reason=f"Ticket closed by {interaction.user.name}")
        except Exception as e:
            err_log = Logs(category=Channels.LOGS_TECHNICAL, message=f"Error while deleting ticket channel ({interaction.channel.id}): {e}", color=LogsColor.RED)
            await err_log.send_log(interaction.client)
            await interaction.followup.send("Wystąpił błąd przy usuwaniu tego kanału.", ephemeral=True)


class CloseReasonModal(Modal, title="Zamknij ticket"):
    reason = TextInput(label="Powód zamknięcia", style=discord.TextStyle.paragraph, placeholder="Podaj powód zamknięcia ticketu...", required=True, max_length=1000)

    async def on_submit(self, interaction: discord.Interaction):
        await handle_close_ticket(interaction, reason=self.reason.value)


class TicketControlsView(View):
    def __init__(self):
        super().__init__(timeout=None)

    @discord.ui.button(label="Zamknij ticket", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket")
    async def close_ticket(self, interaction: discord.Interaction, button: Button):
        await handle_close_ticket(interaction)

    @discord.ui.button(label="Zamknij ticket z powodem", style=discord.ButtonStyle.danger, emoji="🔒", custom_id="close_ticket_with_reason")
    async def close_ticket_with_reason(self, interaction: discord.Interaction, button: Button):
        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
            return

        ticket_data = get_ticket(interaction.channel.id)
        ticket_category = ticket_data.get("category") if ticket_data else None

        if not await can_manage_ticket(interaction.guild, interaction.user.id, ticket_category):
            await interaction.response.send_message("Nie masz uprawnień do zamknięcia z powodem.", ephemeral=True)
            return

        await interaction.response.send_modal(CloseReasonModal())


async def handle_close_ticket(interaction: discord.Interaction, reason: Optional[str] = None):
    guild = interaction.guild
    channel = interaction.channel

    if not guild or not isinstance(channel, discord.TextChannel):
        await interaction.response.send_message("Nie można użyć tej komendy tutaj.", ephemeral=True)
        return

    if not interaction.response.is_done():
        await interaction.response.defer()

    ticket_data = get_ticket(channel.id)
    creator_id = ticket_data.get("creator_id") if ticket_data else None
    ticket_category = ticket_data.get("category") if ticket_data else None

    users_removed = []

    for target, override in getattr(channel, "overwrites", {}).items():
        if isinstance(target, discord.Member):
            if not await can_manage_ticket(guild, target.id, ticket_category):
                await channel.set_permissions(target, overwrite=None)
                users_removed.append(f"<@{target.id}>")

    users_str = "\n".join(users_removed) if users_removed else "Brak"

    embed = create_closed_embed(channel.id, interaction.user.id, users_str)
    view = ConfirmCloseView()

    await channel.send(embed=embed, view=view)

    if reason and creator_id:
        creator = guild.get_member(creator_id)
        is_doj_ticket = ticket_data.get("category") == "doj" if ticket_data else False
        closer_role_name = "członka Departamentu Sprawiedliwości" if is_doj_ticket else "administratora"

        if creator:
            try:
                await creator.send(f"Twój ticket został zamknięty przez {closer_role_name}: **{interaction.user.name}** z powodem: {reason}")
            except discord.Forbidden:
                dm_log = Logs(
                    category=Channels.LOGS_TICKET,
                    message=f"Nie udało się wysłać wiadomości DM o zamknięciu ticketu do <@{creator_id}>, ponieważ ma wyłączone wiadomości prywatne.",
                    color=LogsColor.YELLOW,
                )
                await dm_log.send_log(interaction.client)

        log = Logs(
            category=Channels.LOGS_TICKET,
            message=f"Ticket <#{channel.id}> został wstępnie zamknięty (z powodem) przez <@{interaction.user.id}>\nAutor ticketu: <@{creator_id}>\nPowód: {reason}",
            color=LogsColor.RED,
        )
        await log.send_log(interaction.client)
    else:
        log = Logs(
            category=Channels.LOGS_TICKET,
            message=f"Ticket <#{channel.id}> został wstępnie zamknięty przez <@{interaction.user.id}>\nAutor ticketu: <@{creator_id}>",
            color=LogsColor.NEUTRAL,
        )
        await log.send_log(interaction.client)


class Ticket:
    """
    Represents a support ticket in the system.
    """

    def __init__(
        self,
        author: Union[discord.User, discord.Member],
        category: str,
        channel_id: Optional[Union[int, discord.TextChannel]],
        guild_id: Union[int, discord.Guild],
    ):

        self.author = author
        self.category = category
        self.allowed_users: List[Union[discord.User, discord.Member, discord.Role]] = [author]
        self.channel_id = channel_id
        self.guild_id = guild_id

    async def create_ticket(self, interaction: discord.Interaction):
        """
        Creates a new ticket channel with the appropriate permissions.
        """
        guild = interaction.guild
        if not guild:
            return None

        channel_id_int = self.channel_id.id if isinstance(self.channel_id, discord.TextChannel) else self.channel_id
        base_channel = guild.get_channel(channel_id_int) if channel_id_int else None

        category_channel = base_channel.category if isinstance(base_channel, discord.TextChannel) and base_channel else None

        overwrites = {
            guild.default_role: discord.PermissionOverwrite(read_messages=False),
            self.author: discord.PermissionOverwrite(read_messages=True, send_messages=True),
        }

        admin_role = guild.get_role(Roles.ADMIN)
        if admin_role:
            overwrites[admin_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            self.allowed_users.append(admin_role)

        adex = guild.get_member(Users.ADEX)
        if adex:
            overwrites[adex] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            self.allowed_users.append(adex)

        heryod = guild.get_member(Users.HERYOD)
        if heryod:
            overwrites[heryod] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
            self.allowed_users.append(heryod)

        if self.category == "doj":
            doj_role = guild.get_role(Roles.DOJ)
            if doj_role:
                overwrites[doj_role] = discord.PermissionOverwrite(read_messages=True, send_messages=True)
                self.allowed_users.append(doj_role)
            doj_category = guild.get_channel(Categories.DOJ_TICKETS)
            if doj_category and isinstance(doj_category, discord.CategoryChannel):
                category_channel = doj_category

        _, standard_options = create_ticket_embed()
        _, doj_options = create_doj_ticket_embed()
        all_options = standard_options + doj_options

        emoji = "🎫"
        for opt in all_options:
            if opt["value"] == self.category:
                emoji = str(opt["emoji"]) if opt.get("emoji") else "🎫"
                break

        category_mappings = {"other": "inne", "report_player": "zgloszenie", "technical_issue": "blad", "doj": "doj"}
        mapped_category = category_mappings.get(self.category, self.category)

        channel_name = f"{emoji}-{mapped_category}-{self.author.name}"

        ticket_channel = await guild.create_text_channel(name=channel_name, category=category_channel, overwrites=overwrites)

        if self.category == "doj":
            welcome_embed = create_doj_welcome_embed()
        else:
            welcome_embed = create_welcome_embed()

        controls_view = TicketControlsView()
        await ticket_channel.send(content=f"{self.author.mention}", embed=welcome_embed, view=controls_view)

        ticket_data = {
            "ticket_id": ticket_channel.id,
            "creator_id": self.author.id,
            "category": self.category,
            "status": "open",
            "created_at": datetime.now().isoformat(),
        }
        save_ticket(ticket_data)

        open_log = Logs(
            category=Channels.LOGS_TICKET,
            message=f"Utworzono nowy ticket <#{ticket_channel.id}> przez <@{self.author.id}>\nKategoria: {self.category}",
            color=LogsColor.GREEN,
        )
        await open_log.send_log(interaction.client)

        return ticket_channel


class TicketButton(discord.ui.Button):
    """Button for ticket creation"""

    def __init__(self, label: str, custom_id: str, emoji: str, style: discord.ButtonStyle, cog):
        super().__init__(label=label, custom_id=f"ticket_{custom_id}", emoji=emoji, style=style)
        self.cog = cog
        self.category_value = custom_id

    async def callback(self, interaction: discord.Interaction):
        """handler for user click - creates a ticket"""
        if not interaction.guild:
            await interaction.response.defer()
            return

        member = interaction.user

        if get_user_ticket_count(member.id) >= 5:
            log = Logs(
                category=Channels.LOGS_SECURITY,
                message=f"Użytkownik <@{member.id}> próbował utworzyć kolejny ticket, ale osiągnął już limit 5 otwartych ticketów.",
                color=LogsColor.YELLOW,
            )
            await log.send_log(interaction.client)
            await interaction.followup.send("Masz już ponad 5 otwartych ticketów! Zamknij poprzednie, aby móc otworzyć nowy.", ephemeral=True)
            return

        ticket = Ticket(
            author=member,
            category=self.category_value,
            channel_id=interaction.channel_id,
            guild_id=interaction.guild.id,
        )
        ticket_channel = await ticket.create_ticket(interaction)

        if ticket_channel:
            await interaction.response.defer()
            await interaction.followup.send(f"Twój ticket w kategorii {self.category_value} został utworzony: {ticket_channel.mention}", ephemeral=True)
        else:
            await interaction.followup.send("Nie udało się utworzyć ticketu. Brak dostępu do serwera.", ephemeral=True)


class TicketPersistentView(View):
    """Persistent view for the ticket system panel"""

    def __init__(self, options, cog):
        super().__init__(timeout=None)
        for opt in options:
            self.add_item(TicketButton(label=opt["label"], custom_id=opt["value"], emoji=opt["emoji"], style=opt["style"], cog=cog))


class TicketCog(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot
        _, self.ticket_options = create_ticket_embed()
        _, self.doj_options = create_doj_ticket_embed()

        self.bot.add_view(TicketPersistentView(self.ticket_options, self))
        self.bot.add_view(TicketPersistentView(self.doj_options, self))

        self.bot.add_view(TicketControlsView())
        self.bot.add_view(ConfirmCloseView())

    @app_commands.command(name="ticket-panel", description="Wysyła panel systemu ticketów")
    async def ticketPanel(self, interaction: discord.Interaction):
        """Slash command that sends the ticket system panel"""

        if not Permissions.is_high_admin(interaction.user.id):
            await interaction.response.send_message("Nie masz uprawnień do użycia tej komendy.", ephemeral=True)
            return

        embed, options = create_ticket_embed()
        view = TicketPersistentView(options, self)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="ticket-doj-panel", description="Wysyła panel systemu ticketów DOJ")
    async def ticketDojPanel(self, interaction: discord.Interaction):
        """Slash command that sends the DOJ ticket system panel"""

        if not Permissions.is_high_admin(interaction.user.id):
            await interaction.response.send_message("Nie masz uprawnień do użycia tej komendy.", ephemeral=True)
            return

        embed, options = create_doj_ticket_embed()
        view = TicketPersistentView(options, self)
        await interaction.response.send_message(embed=embed, view=view)

    @app_commands.command(name="dodaj", description="Dodaje użytkownika do obecnego ticketu")
    @app_commands.describe(user="Użytkownik do dodania")
    async def add_user_to_ticket(self, interaction: discord.Interaction, user: discord.Member):
        """Slash command that adds a user to the current ticket"""
        if not interaction.guild or not isinstance(interaction.channel, discord.TextChannel):
            await interaction.response.send_message("Tej komendy można użyć tylko na kanale.", ephemeral=True)
            return

        ticket_data = get_ticket(interaction.channel.id)
        if not ticket_data:
            await interaction.response.send_message("Ta komenda może być użyta tylko na kanale ticketu.", ephemeral=True)
            return

        ticket_category = ticket_data.get("category")
        is_creator = ticket_data.get("creator_id") == interaction.user.id
        is_manager = await can_manage_ticket(interaction.guild, interaction.user.id, ticket_category)

        if not (is_creator or is_manager):
            await interaction.response.send_message("Nie masz uprawnień, aby dodawać osoby do tego ticketu.", ephemeral=True)
            return

        await interaction.channel.set_permissions(user, read_messages=True, send_messages=True)
        await interaction.response.send_message(f"Pomyślnie dodano użytkownika {user.mention} do ticketu.")

        log = Logs(
            category=Channels.LOGS_TICKET,
            message=f"Użytkownik <@{interaction.user.id}> dodał <@{user.id}> do ticketu <#{interaction.channel.id}> (Kategoria: {ticket_category})",
            color=LogsColor.BLUE,
        )
        await log.send_log(interaction.client)


async def setup(bot: commands.Bot):
    """Function needed to load the cog."""
    await bot.add_cog(TicketCog(bot))
