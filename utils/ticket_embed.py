from discord import Embed, SelectOption
import discord


def create_ticket_embed() -> tuple[Embed, list[dict]]:
    """
    Creates an embed for the ticket channel with relevant information.
    """
    embed = discord.Embed(
        title="Utwórz ticket",
        description="Kliknij przycisk aby utworzyć ticket.",
        colour=0x23B710,
    )

    embed.set_author(name="EasyLife - Ticket System")

    embed.add_field(
        name="Regulamin ticketów:",
        value='1. Tickety typu "Adex obczaj pv" będą automatycznie zamykane.\n2. Nie prowadzimy sprzedaży usług/rang poprzez tickety (kontakt priv Adex)\n3. Po utworzeniu ticketu, czekaj cierpliwie na odpowiedź administracji.\n4. Zalecamy użyć ticketów do zgłaszania wszelkich błędów/spraw serwerowych.\n5. Opisz dokładnie całą sprawę tak aby administrator nie musiał się niczego dopytywać.\n',
        inline=False,
    )
    embed.add_field(
        name="Zalecamy używania ticketów do:",
        value="- Zgłaszania błędów serwerowych\n- Zgłaszania ogólnych spraw do administracji serwera\n- Zgłaszania spraw związanych z forum serwera",
        inline=False,
    )

    options = [
        {
            "label": "Zgłoś gracza",
            "value": "report_player",
            "emoji": "📫",
            "style": discord.ButtonStyle.primary,
        },
        {
            "label": "Znalazłem błąd",
            "value": "technical_issue",
            "emoji": "🛠️",
            "style": discord.ButtonStyle.danger,
        },
        {
            "label": "Mam inną sprawę",
            "value": "other",
            "emoji": "❔",
            "style": discord.ButtonStyle.secondary,
        },
    ]

    return embed, options


def create_doj_ticket_embed() -> tuple[discord.Embed, list[dict]]:
    """
    Creates an embed for the DOJ ticket channel.
    """
    embed = discord.Embed(
        title="Zgłoszenie do Departamentu Sprawiedliwości",
        description="Tickety to forma zgłoszeń do Departamentu Sprawiedliwości **(IC)**.\n\nOtwórz ticket, jeśli chcesz zgłosić sprawę do Sądu lub masz pytanie związane z jego działaniem.",
        color=0xD78207,
    )

    embed.set_author(name="DOJ - TicketSystem")

    options = [
        {
            "label": "Otwórz Ticket",
            "value": "doj",
            "emoji": "🗄️",
            "style": discord.ButtonStyle.secondary,
        }
    ]

    return embed, options


def create_welcome_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Ticket",
        description="Dziekujemy za skontaktowanie się z administracją!\nPamiętaj aby przestrzegać regulamin ticketów który znajdziesz na kanale <#1199881479153528872>",
        color=6997023,
    )
    embed.set_author(name="EasyLife - Ticket System")
    return embed


def create_doj_welcome_embed() -> discord.Embed:
    embed = discord.Embed(
        title="Ticket",
        description="Witamy w oficjalnej drodze komunikacji z Departamentem Sprawiedliwości.\n\nTutaj możesz zgłosić sprawę do Sądu lub zadać nam pytanie.",
        color=0x4DDC18,
    )
    embed.set_author(name="Departament Sprawiedliwości - Ticket")
    return embed


def create_closed_embed(channel_id: int, user_id: int, users_str: str) -> discord.Embed:
    from datetime import datetime

    embed = discord.Embed(
        title="Zamknięto ticket",
        description=f"Ticket <#{channel_id}> ID: **{channel_id}** został zamknięty przez użytkownika: <@{user_id}>\nZabrano dostęp do kanału użytkownikom:\n\n {users_str}",
        color=0xFC0F00,
    )
    embed.timestamp = datetime.now()
    return embed
