# بوت المكتبة التعليمية الجامعية

## Overview
This project is a Telegram bot designed to manage a university educational library. Its primary purpose is to allow users to browse sections and files, as well as contribute content. The bot aims to streamline access to educational resources, provide a structured content organization system, and facilitate user contributions within a university setting.

## User Preferences
I prefer that the agent adheres strictly to the defined architectural patterns and project structure. All user-facing texts should be managed dynamically through the `text_entries` table. I also prefer that administrative actions are thoroughly logged using the audit log system. For UI/UX, ensure that all buttons have appropriate emojis and confirmation messages are clear, especially for destructive actions. When displaying files, categorize them with relevant emojis.

#
# System Architecture

### Core Technologies
The bot is built with **Python 3.11**, utilizing **aiogram** for Telegram bot interactions, **SQLAlchemy** as the ORM for database operations, **asyncpg** for asynchronous PostgreSQL connectivity, and **Alembic** for database migrations.

### Project Structure
The project is organized into modular components:
- `bot/core/`: Contains fundamental configurations (config, constants, database connection, logging).
- `bot/handlers/`: Manages all message and command handlers, including home, sections, files, search, and fallback.
- `bot/middlewares/`: Implements various middleware for features like ban checks, subscription enforcement, role management, user tracking, and internationalization.
- `bot/models/`: Defines all database models (User, TextEntry, Setting, AuditLog, Section, File, FileSection).
- `bot/modules/`: Houses central bot functionalities such as central routing, error handling, health checks, and login logging.
- `bot/services/`: Provides business logic and abstractions for i18n, state management, user operations, seeding default data, permissions, audit logging, section management, and file management.
- `bot/utils/`: Contains utility functions.
- `migrations/`: Stores Alembic migration scripts.
- `main.py`: The application entry point.

### UI/UX Decisions
- All buttons incorporate relevant emojis (e.g., 📁 for sections, 📄 for files, ✅ for confirmation).
- Files are displayed with emojis corresponding to their type (e.g., 📄 for documents, 🖼 for photos, 🎬 for videos).
- Confirmation and deletion messages include clear warnings.
- Header texts are formatted using HTML bold.
- Pagination is implemented for file browsing, showing 5 files per page with navigation buttons.

### Feature Specifications

#### Dynamic Texts and Localization
All user-facing texts are managed dynamically via the `text_entries` database table, accessible through the `I18nService`. Internal logging and error messages are defined in `constants.py`.

#### Roles and Permissions System
A robust role-based access control (RBAC) system is implemented:
- **Roles**: `user`, `moderator`, `admin`.
- **Permissions**: Defined in `permissions.py`, mapping roles to specific capabilities (e.g., `browse`, `upload_file`, `manage_sections`, `manage_users`).
- Permissions are checked programmatically using `has_permission(role, permission)` and with user notifications using `check_permission_and_notify`.
- Administrative buttons are dynamically hidden or shown based on the user's role.

#### Audit Log
All administrative actions (create, edit, delete sections/files) are recorded in the `audit_logs` table via `AuditService`. `AuditActions` are defined in `constants.py`.

#### Section Management
- Supports nested sections using a `parent_id` for hierarchical organization.
- Sections have `name`, `description`, `order`, and `is_active` fields.
- Logical deletion is implemented by setting `is_active = False`.
- Administrative FSMs (Finite State Machines) are used for adding, editing, and ordering sections.
- Callback prefixes are standardized for section-related actions (e.g., `sec:{id}`, `sec_add:{parent_id}`).

#### File Management
- Supports various file types (DOCUMENT, PHOTO, VIDEO, AUDIO, etc.).
- Files are linked to sections via a many-to-many relationship (`FileSection`).
- Duplicate file detection is implemented using `file_unique_id`.
- Files have `file_id` (Telegram's file ID), `name`, `file_type`, `file_size`, `status` (PENDING, PUBLISHED), and `uploaded_by`.
- Files are logically deleted (`is_active = False`).
- An FSM handles the file upload process, allowing users to send multiple files.
- Uploaded files are forwarded to a dedicated storage channel (`STORAGE_CHANNEL_ID`) and their Telegram `file_id` is stored.
- Files within a section are automatically sent to the user upon entering the section, respecting Telegram's rate limits.
- Deep linking is supported for direct file access (e.g., `t.me/bot?start=file_<id>`).

#### Search Module
- Users access search via the "🔍 البحث" button on the home screen.
- Search covers section names and file names (published and active only).
- Partial match, case-insensitive, using SQL `LOWER(name) LIKE '%query%'`.
- Maximum 20 results per type (sections + files).
- Results displayed with clear type distinction: 📁 for sections, 📄 for files.
- Selecting a section opens it directly; selecting a file sends it to the user.
- Search uses an independent FSM state (`search_input`) that doesn't affect browsing state.
- Back button clears search state and returns to home.
- Minimum 2 characters required for search query.
- Callback prefixes: `sr_sec:{id}`, `sr_file:{id}`, `sr_back`.

### Architectural Principles
- **Modularity**: Code is organized into logical units (handlers, middlewares, services).
- **Dynamic Content**: All user-facing texts are externalized to the database for easy management and localization.
- **Centralized Routing**: All callback queries are processed through a `CentralRouter`.
- **Middleware Chain**: Middlewares are executed in a specific order: ban check → subscription check → user tracking → role check → i18n.
- **State Management**: Each user has a single state with a configurable timeout.
- **Ordered Routers**: Routers are prioritized to handle specific interactions effectively (home → files → search → sections → central → fallback).

## External Dependencies

- **Telegram Bot API**: Accessed via `aiogram` for all bot interactions.
- **PostgreSQL**: The primary database for storing all application data.
- **Alembic**: Used for managing and applying database schema migrations.
- **External Storage Channel (Telegram)**: A designated Telegram channel (`STORAGE_CHANNEL_ID`) is used to store uploaded files, leveraging Telegram's infrastructure for content hosting.
- **Mandatory Subscription Channels (Telegram)**: Configurable Telegram channels (`SUBSCRIPTION_CHANNEL_IDS`) that users must join to use the bot.