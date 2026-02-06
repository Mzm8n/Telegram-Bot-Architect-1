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
    HANDLERS_REGISTERED = "All handlers registered"

    START_COMMAND = "Start command from user {user_id}"
    HOME_DISPLAYED = "Home displayed for user {user_id}"
    BUTTON_PRESSED = "Button pressed: {button} by user {user_id}"
    BACK_PRESSED = "Back pressed by user {user_id}"
    UNKNOWN_TEXT = "Unknown text from user {user_id}"


class ErrorMessages:
    DATABASE_NOT_INITIALIZED = "Database not initialized"
    I18N_NOT_INITIALIZED = "I18n service not initialized"
    STATE_NOT_INITIALIZED = "State service not initialized"


class CallbackPrefixes:
    HOME = "home"
    SECTIONS = "sections"
    SEARCH = "search"
    CONTRIBUTE = "contribute"
    ABOUT = "about"
    CONTACT = "contact"
    TOOLS = "tools"
    BACK = "back"


class I18nKeys:
    ERROR_GENERAL = "error.general"
    ERROR_BLOCKED = "error.blocked"
    ERROR_SUBSCRIPTION_REQUIRED = "error.subscription_required"
    ERROR_PERMISSION_DENIED = "error.permission_denied"
    ERROR_STATE_EXPIRED = "error.state_expired"

    LOGIN_NOTIFICATION = "login.notification"

    HOME_WELCOME = "home.welcome"
    HOME_BTN_SECTIONS = "home.btn.sections"
    HOME_BTN_SEARCH = "home.btn.search"
    HOME_BTN_CONTRIBUTE = "home.btn.contribute"
    HOME_BTN_ABOUT = "home.btn.about"
    HOME_BTN_CONTACT = "home.btn.contact"
    HOME_BTN_TOOLS = "home.btn.tools"
    HOME_BTN_BACK = "home.btn.back"

    HOME_ABOUT_TEXT = "home.about.text"
    HOME_CONTACT_TEXT = "home.contact.text"
    HOME_PLACEHOLDER = "home.placeholder"
    HOME_UNKNOWN_TEXT = "home.unknown_text"


class DefaultTexts:
    TEXTS = {
        "error.general": "حدث خطأ غير متوقع. يرجى المحاولة لاحقاً.",
        "error.blocked": "تم حظرك من استخدام البوت.",
        "error.subscription_required": "يجب الاشتراك في القناة أولاً للاستمرار.",
        "error.permission_denied": "ليس لديك صلاحية للقيام بهذا الإجراء.",
        "error.state_expired": "انتهت مهلة العملية. يرجى المحاولة مرة أخرى.",
        "login.notification": "تسجيل دخول جديد:\nالمعرف: {user_id}\nالاسم: {name}\nالوقت: {time}\nاسم المستخدم: {username}",
        "home.welcome": "مرحباً {name}!\nاختر من القائمة:",
        "home.btn.sections": "الأقسام",
        "home.btn.search": "البحث",
        "home.btn.contribute": "مساهمة بملف",
        "home.btn.about": "عن البوت",
        "home.btn.contact": "تواصل مع المطور",
        "home.btn.tools": "أدوات وميزات",
        "home.btn.back": "رجوع",
        "home.about.text": "بوت المكتبة التعليمية الجامعية\nيتيح لك تصفح الأقسام والملفات والمساهمة بالمحتوى.",
        "home.contact.text": "للتواصل مع المطور يرجى مراسلة الحساب التالي.",
        "home.placeholder": "هذه الميزة قيد التطوير وستكون متاحة قريباً.",
        "home.unknown_text": "لم أفهم رسالتك. يرجى استخدام الأزرار أدناه.",
    }
