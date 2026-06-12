# EasyLife Discord Bot

Dedykowany bot Discord dla społeczności EasyLife, przygotowany do obsługi jednego, konkretnego serwera.

Projekt skupia się na trzech głównych obszarach:
- system ticketów (w tym osobny panel DOJ),
- zarządzanie rolami (self-role i role administracyjne),
- status bota oparty o stan serwera Minecraft.

## Przeznaczenie projektu

Ten bot jest stworzony pod **jeden serwer Discord** i jego konkretne ID/role/kanały.

W kodzie znajdują się stałe z ID:
- serwera (`GUILD_ID`),
- ról,
- kanałów logów,
- kategorii ticketów,
- użytkowników z najwyższymi uprawnieniami.

Oznacza to, że bot nie jest projektem multi-tenant i nie jest przygotowany do obsługi wielu serwerów jednocześnie bez modyfikacji konfiguracji.

## Główne funkcje

### 1. System ticketów

Bot obsługuje dwa panele ticketowe:
- standardowy panel administracyjny,
- panel DOJ (Departament Sprawiedliwości).

Po utworzeniu ticketu:
- tworzony jest osobny kanał tekstowy,
- ustawiane są odpowiednie uprawnienia widoczności,
- wysyłana jest wiadomość powitalna z przyciskami kontroli,
- ticket zapisywany jest do `data/tickets.json`,
- akcja jest logowana na kanał logów ticketów.

Obsługiwane kategorie ticketów:
- `report_player` (zgłoszenie gracza),
- `technical_issue` (zgłoszenie błędu),
- `other` (inna sprawa),
- `doj` (zgłoszenia DOJ).

Dodatkowe zasady działania:
- limit: maksymalnie 5 otwartych ticketów na użytkownika,
- możliwość dodania użytkownika do aktywnego ticketu,
- zamykanie ticketu z opcjonalnym powodem,
- etap zamknięcia z potwierdzeniem usunięcia kanału,
- logowanie działań (otwarcie, dodanie użytkownika, zamknięcie, błędy),
- próba wysłania DM do autora ticketu przy zamknięciu z powodem.

### 2. Role self-service (panel ról)

Bot udostępnia panel wyboru ról przez select menu.

Użytkownik może samodzielnie przełączać role powiadomień:
- `events_ping`,
- `leaks_ping`.

Ponowne wybranie tej samej opcji działa jak toggle (dodanie/usunięcie roli).

### 3. Role administracyjne czasowe i stałe

Dostępne są komendy administracyjne do nadawania i usuwania wybranych ról:
- `PREMIUM`,
- `LEAKS_PING`,
- `EVENTS_PING`.

Można nadać rolę z czasem wygaśnięcia (np. `7d`, `24h`, `30m`).

Informacje o nadaniach i wygaśnięciach są zapisywane do `data/roles.json`.

Przy starcie bota wykonywana jest kontrola wygasłych ról:
- wygasłe role są usuwane automatycznie,
- usunięcia są logowane.

### 4. Dynamiczny status bota

Status bota odświeża się cyklicznie (co 60 sekund).

Tryby statusu:
- niestandardowy tekst ustawiany komendą,
- tryb `players` pokazujący liczbę graczy online z serwera `easylife2.pl`.

Wartość statusu jest zapisywana w `data/status.json`.

## Komendy slash

### Tickety
- `/ticket-panel` - wysyła standardowy panel ticketów.
- `/ticket-doj-panel` - wysyła panel ticketów DOJ.
- `/dodaj user:<użytkownik>` - dodaje użytkownika do aktualnego ticketu.

### Role
- `/role-panel` - wysyła panel self-role (select menu).
- `/rola user:<użytkownik> role:<rola> [time:<czas>]` - nadaje rolę (opcjonalnie czasowo).
- `/rola-usun user:<użytkownik> role:<rola>` - usuwa rolę.

### Status
- `/status [tekst]` - ustawia status bota; bez parametru przełącza na tryb `players`.

## Uprawnienia

W projekcie są dwa poziomy uprawnień:
- **High Admin** - konkretni użytkownicy zdefiniowani w stałych (`Users.HERYOD`, `Users.ADEX`),
- **Staff** - High Admin lub użytkownik z rolą `Roles.ADMIN`.

Komendy paneli (`/ticket-panel`, `/ticket-doj-panel`, `/role-panel`, `/status`) są przeznaczone dla High Admin.

Komendy administracji rolami (`/rola`, `/rola-usun`) wymagają Staff.

Operacje w ticketach (dodawanie, zamykanie) są dodatkowo sprawdzane kontekstowo, w tym specjalna obsługa ticketów DOJ.

## Logowanie

Bot korzysta z systemu logów embedowych i kieruje zdarzenia na dedykowane kanały, m.in.:
- logi ogólne,
- logi ról,
- logi ticketów,
- logi bezpieczeństwa,
- logi techniczne.

Dzięki temu działania administracyjne i problemy techniczne są śledzone w czasie rzeczywistym.

## Struktura projektu

Najważniejsze katalogi:
- `cogs/` - moduły komend i funkcji bota,
- `config/` - stałe i konfiguracja środowiska,
- `utils/` - funkcje pomocnicze (embedy, status, obsługa plików),
- `logs/` - logika wysyłania logów,
- `data/` - dane trwałe (`roles.json`, `status.json`, `tickets.json`).

## Instalacja i uruchomienie

### 1. Wymagania
- Python 3.12,
- token bota Discord,
- poprawnie ustawione ID ról/kanałów/kategorii pod Twój serwer.

### 2. Instalacja zależności
```bash
pip install -r requirements.txt
```

### 3. Konfiguracja środowiska
Utwórz plik `.env` i ustaw:
```env
DISCORD_TOKEN=twoj_token_bota
```

`GUILD_ID` i pozostałe ID są obecnie zapisane na stałe w kodzie (`config/config.py`, `config/constants.py`).

### 4. Uruchomienie bota
```bash
python main.py
```

### 5. Synchronizacja komend (opcjonalnie)
Jeśli chcesz ręcznie wymusić synchronizację slash komend:
```bash
python sync_commands.py
```

## Uwagi końcowe

To repozytorium jest celowo dopasowane do jednego serwera EasyLife.

Jeśli chcesz użyć projektu na innym serwerze, trzeba dostosować:
- ID ról,
- ID kanałów i kategorii,
- ID użytkowników z najwyższymi uprawnieniami,
- ewentualnie opisy i treści embedów.
