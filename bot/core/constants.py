class LogMessages:
    STARTING_BOT = "Starting bot..."
    DATABASE_URL_NOT_SET = "DATABASE_URL not set"
    CONNECTING_TO_DATABASE = "Connecting to database..."
    DATABASE_CONNECTED = "Database connected"
    BOT_TOKEN_NOT_SET = "BOT_TOKEN not set - running in test mode"
    INFRASTRUCTURE_READY = "Infrastructure ready"
    BOT_READY = "Bot ready"
    BOT_STOPPED = "Bot stopped"

    I18N_LOADED = "I18n texts loaded from database"
    I18N_RELOADED = "I18n texts reloaded"
    I18N_SEEDED = "I18n default texts seeded"

    STATE_EXPIRED = "State expired for user {user_id}"
    STATE_SET = "State set for user {user_id}: {state}"
    STATE_CLEARED = "State cleared for user {user_id}"
    STATES_CLEANUP = "Cleaned up {count} expired states"

    USER_CREATED = "New user created: {user_id}"
    USER_LOGIN = "User login: {user_id}"
    USER_BLOCKED = "Blocked user {user_id} attempted access"

    MIDDLEWARE_BAN_CHECK = "Ban check for user {user_id}"
    MIDDLEWARE_SUBSCRIPTION_CHECK = "Subscription check for user {user_id}"
    MIDDLEWARE_ROLE_LOADED = "Role loaded for user {user_id}: {role}"

    ERROR_HANDLER_TRIGGERED = "Error in handler: {error}"
    HEALTH_CHECK_OK = "Health check: OK"
    HEALTH_CHECK_FAIL = "Health check: FAIL - {reason}"

    CENTRAL_ROUTER_REGISTERED = "Central router registered"
    CENTRAL_ROUTER_CALLBACK = "Callback received: {callback_data}"
    CENTRAL_ROUTER_NO_HANDLER = "No handler for callback: {callback_data}"

    SERVICES_INITIALIZED = "All services initialized"
    MIDDLEWARES_REGISTERED = "All middlewares registered"


class ErrorMessages:
    DATABASE_NOT_INITIALIZED = "Database not initialized"
    I18N_NOT_INITIALIZED = "I18n service not initialized"
    STATE_NOT_INITIALIZED = "State service not initialized"


class I18nKeys:
    ERROR_GENERAL = "error.general"
    ERROR_BLOCKED = "error.blocked"
    ERROR_SUBSCRIPTION_REQUIRED = "error.subscription_required"
    ERROR_PERMISSION_DENIED = "error.permission_denied"
    ERROR_STATE_EXPIRED = "error.state_expired"

    LOGIN_NOTIFICATION = "login.notification"


class DefaultTexts:
    TEXTS = {
        "error.general": "عذراً، حدث خطأ غير متوقع. يرجى المحاولة لاحقاً.",
        "error.blocked": "عذراً، تم حظرك من استخدام البوت.",
        "error.subscription_required": "يجب الاشتراك في القناة أولاً للاستمرار.",
        "error.permission_denied": "ليس لديك صلاحية للقيام بهذا الإجراء.",
        "error.state_expired": "انتهت مهلة العملية. يرجى المحاولة مرة أخرى.",
        "login.notification": "تسجيل دخول جديد:\nالمعرف: {user_id}\nالاسم: {name}\nالوقت: {time}\nاسم المستخدم: {username}",
    }
