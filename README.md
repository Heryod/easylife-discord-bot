# EasyLife Discord Bot

A dedicated Discord bot for the EasyLife community, designed to serve one specific server.

The project focuses on three main areas:
- ticket system (including a separate DOJ panel),
- role management (self-service and administrative roles),
- bot status based on the Minecraft server status.

## Project Purpose

This bot is built for **a single Discord server** and its specific IDs, roles, and channels.

The code contains constants for the IDs of:
- the server (`GUILD_ID`),
- roles,
- log channels,
- ticket categories,
- users with the highest permissions.

This means the bot is not a multi-tenant project and is not designed to serve multiple servers simultaneously without configuration changes.

## Main Features

### 1. Ticket System

The bot supports two ticket panels:
- standard administrative panel,
- DOJ (Department of Justice) panel.

When a ticket is created:
- a separate text channel is created,
- appropriate visibility permissions are set,
- a welcome message with control buttons is sent,
- the ticket is saved to `data/tickets.json`,
- the action is logged to the ticket log channel.

Supported ticket categories:
- `report_player` (player report),
- `technical_issue` (bug report),
- `other` (other inquiry),
- `doj` (DOJ requests).

Additional behavior:
- limit of 5 open tickets per user,
- ability to add a user to an active ticket,
- ticket closure with an optional reason,
- a closure step that confirms channel deletion,
- action logging (opening, adding a user, closing, errors),
- an attempt to send a DM to the ticket author when closing with a reason.

### 2. Self-Service Roles (Role Panel)

The bot provides a role selection panel using a select menu.

Users can toggle notification roles themselves:
- `events_ping`,
- `leaks_ping`.

Selecting the same option again toggles the role (adds or removes it).

### 3. Temporary and Permanent Administrative Roles

Administrative commands are available to assign and remove selected roles:
- `PREMIUM`,
- `LEAKS_PING`,
- `EVENTS_PING`.

Roles can be assigned with an expiration time (for example, `7d`, `24h`, `30m`).

Role assignments and expirations are saved to `data/roles.json`.

When the bot starts, it checks for expired roles:
- expired roles are removed automatically,
- removals are logged.

### 4. Dynamic Bot Status

The bot status is refreshed periodically (every 60 seconds).

Status modes:
- custom text set with a command,
- `players` mode, which shows the number of players online on the `easylife2.pl` server.

The status value is saved to `data/status.json`.

## Slash Commands

### Tickets
- `/ticket-panel` - sends the standard ticket panel.
- `/ticket-doj-panel` - sends the DOJ ticket panel.
- `/dodaj user:<user>` - adds a user to the current ticket.

### Roles
- `/role-panel` - sends the self-service role panel (select menu).
- `/rola user:<user> role:<role> [time:<duration>]` - assigns a role, optionally for a limited time.
- `/rola-usun user:<user> role:<role>` - removes a role.

### Status
- `/status [text]` - sets the bot status; with no parameter, switches to `players` mode.

## Permissions

The project has two permission levels:
- **High Admin** - specific users defined in constants (`Users.HERYOD`, `Users.ADEX`),
- **Staff** - a High Admin or a user with the `Roles.ADMIN` role.

Panel commands (`/ticket-panel`, `/ticket-doj-panel`, `/role-panel`, `/status`) are intended for High Admins.

Role administration commands (`/rola`, `/rola-usun`) require Staff permissions.

Ticket operations (adding users and closing tickets) are also checked in context, including special handling for DOJ tickets.

## Logging

The bot uses an embed-based logging system and sends events to dedicated channels, including:
- general logs,
- role logs,
- ticket logs,
- security logs,
- technical logs.

This keeps administrative actions and technical issues visible in real time.

## Project Structure

Key directories:
- `cogs/` - bot command and feature modules,
- `config/` - constants and environment configuration,
- `utils/` - helper functions (embeds, status, file handling),
- `logs/` - logging implementation,
- `data/` - persistent data (`roles.json`, `status.json`, `tickets.json`).
