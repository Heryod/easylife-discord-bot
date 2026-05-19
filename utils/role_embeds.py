from discord import Embed, SelectOption


def create_role_panel_embed() -> tuple[Embed, list[SelectOption]]:
    """Creates an embed for the role selection panel with relevant information and options."""
    embed = Embed(
        title="Odbierz role:",
        description="Wybierz rolę którą chcesz otrzymać:",
        colour=0x59C3EE,
    )

    embed.set_author(name="EasyLife - SelfRole")

    embed.set_footer(text="(jeżeli chcesz usunąć rolę która wcześniej wybrałeś po prostu naciśnij na nią ponownie)")

    options = [
        SelectOption(
            label="wydarzenia.ping",
            value="events_ping",
            emoji="📅",
            description="Powiadomienia z nowymi wydarzeniami",
        ),
        SelectOption(
            label="Przecieki.ping",
            value="leaks_ping",
            emoji="🤐",
            description="Powiadomienia z nowymi przeciekami",
        ),
    ]

    return embed, options
