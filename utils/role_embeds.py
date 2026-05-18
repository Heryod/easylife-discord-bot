from discord import Embed, SelectOption

def create_role_panel_embed() -> tuple[Embed, list[SelectOption]]:
  """Tworzy embed panelu ról i listę opcji Select"""
  embed = Embed(title="Odbierz role:", description="Wybierz rolę którą chcesz otrzymać:", colour=0x59c3ee)

  embed.set_author(name="EasyLife - SelfRole")

  embed.set_footer(text="(jeżeli chcesz usunąć rolę która wcześniej wybrałeś po prostu nacisnij na nią ponownie)")

  options = [
    SelectOption(
      label="evenimente.ping",
      value="events_ping",
      emoji="📅",
      description="Powiadomienia z nowymi wydarzeniami"
    ),
    SelectOption(
      label="Przecieki.ping",
      value="leaks_ping",
      emoji="🤐",
      description="Powiadomienia z nowymi przeciekami"
    )
  ]

  return embed, options