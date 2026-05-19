from discord import Embed, SelectOption
import discord


def create_ticket_embed() -> tuple[Embed, list[SelectOption]]:
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
        SelectOption(
            label="Zgłoś gracza",
            value="report_player",
            emoji="📫",
            description="Chcę zgłosić innego gracza",
        ),
        SelectOption(
            label="Znalazłem błąd",
            value="technical_issue",
            emoji="🛠️",
            description="Chciałbym zgłosić błąd na serwerze",
        ),
        SelectOption(
            label="Inne",
            value="other",
            emoji="❔",
            description="Mam inną sprawę do administracji",
        ),
    ]

    return embed, options
