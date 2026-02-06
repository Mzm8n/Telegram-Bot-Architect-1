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

    AUDIT_LOG_CREATED = "Audit log: user {user_id} action={action}"
    PERMISSION_DENIED = "Permission denied for user {user_id}: {permission}"
    ROLE_CHANGED = "Role changed for user {user_id}: {old_role} -> {new_role}"

    SECTION_CREATED = "Section created: id={section_id} name={name}"
    SECTION_UPDATED = "Section updated: id={section_id} name={name}"
    SECTION_SOFT_DELETED = "Section soft deleted: id={section_id} name={name}"
    SECTION_VIEWED = "Section viewed: id={section_id} by user {user_id}"

    FILE_CREATED = "File created: id={file_id} name={name} by user {user_id}"
    FILE_DUPLICATE = "Duplicate file detected: unique_id={file_unique_id}"
    FILE_LINKED = "File {file_id} linked to section {section_id}"
    FILE_UNLINKED = "File {file_id} unlinked from section {section_id}"
    FILE_SENT = "File {file_id} sent to user {user_id}"
    FILE_FORWARDED = "File forwarded to storage channel: {file_id}"
    FILE_SOFT_DELETED = "File soft deleted: id={file_id} name={name}"
    MEDIA_GROUP_RECEIVED = "Media group received: {count} files from user {user_id}"
    DEEP_LINK = "Deep link: user {user_id} requested file {file_id}"
    STORAGE_CHANNEL_NOT_SET = "STORAGE_CHANNEL_ID not set - file storage disabled"


class ErrorMessages:
    DATABASE_NOT_INITIALIZED = "Database not initialized"
    I18N_NOT_INITIALIZED = "I18n service not initialized"
    STATE_NOT_INITIALIZED = "State service not initialized"


class AuditActions:
    ROLE_CHANGED = "role_changed"
    USER_BLOCKED = "user_blocked"
    USER_UNBLOCKED = "user_unblocked"
    SETTING_CHANGED = "setting_changed"
    SECTION_CREATED = "section_created"
    SECTION_UPDATED = "section_updated"
    SECTION_DELETED = "section_deleted"
    FILE_UPLOADED = "file_uploaded"
    FILE_DELETED = "file_deleted"
    FILE_LINKED = "file_linked"
    FILE_UNLINKED = "file_unlinked"


class CallbackPrefixes:
    HOME = "home"
    SECTIONS = "sections"
    SECTION_VIEW = "sec:"
    SECTION_BACK = "sec_back:"
    SECTION_ADMIN_ADD = "sec_add:"
    SECTION_ADMIN_EDIT = "sec_edit:"
    SECTION_ADMIN_DELETE = "sec_del:"
    SECTION_ADMIN_CONFIRM_DELETE = "sec_cdel:"
    SECTION_ADMIN_SET_ORDER = "sec_ord:"
    SECTION_ADMIN_CANCEL = "sec_cancel"
    SECTION_ADMIN_SKIP_DESC = "sec_skip_desc"
    FILE_VIEW = "file:"
    FILE_PAGE = "fpage:"
    FILE_UPLOAD = "f_up:"
    FILE_DELETE = "f_del:"
    FILE_CONFIRM_DELETE = "f_cdel:"
    FILE_LINK = "f_link:"
    FILE_UNLINK = "f_unlink:"
    FILE_CANCEL = "f_cancel"
    FILE_DONE = "f_done"
    FILE_PUBLISH = "f_pub:"
    SEARCH = "search"
    CONTRIBUTE = "contribute"
    ABOUT = "about"
    CONTACT = "contact"
    TOOLS = "tools"
    BACK = "back"
    ADMIN_PANEL = "admin_panel"


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

    HOME_BTN_ADMIN_PANEL = "home.btn.admin_panel"
    HOME_ABOUT_TEXT = "home.about.text"
    HOME_CONTACT_TEXT = "home.contact.text"
    HOME_PLACEHOLDER = "home.placeholder"
    HOME_UNKNOWN_TEXT = "home.unknown_text"
    ADMIN_PANEL_TEXT = "admin.panel.text"

    SECTIONS_TITLE = "sections.title"
    SECTIONS_EMPTY = "sections.empty"
    SECTIONS_BTN_BACK = "sections.btn.back"
    SECTIONS_BTN_HOME = "sections.btn.home"

    SECTION_ADMIN_BTN_ADD = "section.admin.btn.add"
    SECTION_ADMIN_BTN_EDIT = "section.admin.btn.edit"
    SECTION_ADMIN_BTN_DELETE = "section.admin.btn.delete"
    SECTION_ADMIN_BTN_ORDER = "section.admin.btn.order"
    SECTION_ADMIN_ENTER_NAME = "section.admin.enter_name"
    SECTION_ADMIN_ENTER_DESC = "section.admin.enter_desc"
    SECTION_ADMIN_BTN_SKIP_DESC = "section.admin.btn.skip_desc"
    SECTION_ADMIN_ENTER_ORDER = "section.admin.enter_order"
    SECTION_ADMIN_SAVED = "section.admin.saved"
    SECTION_ADMIN_UPDATED = "section.admin.updated"
    SECTION_ADMIN_DELETED = "section.admin.deleted"
    SECTION_ADMIN_CONFIRM_DELETE = "section.admin.confirm_delete"
    SECTION_ADMIN_BTN_CONFIRM = "section.admin.btn.confirm"
    SECTION_ADMIN_BTN_CANCEL = "section.admin.btn.cancel"
    SECTION_ADMIN_CANCELLED = "section.admin.cancelled"
    SECTION_ADMIN_NOT_FOUND = "section.admin.not_found"
    SECTION_ADMIN_HAS_CHILDREN = "section.admin.has_children"
    SECTION_ADMIN_ENTER_NEW_NAME = "section.admin.enter_new_name"
    SECTION_ADMIN_INVALID_ORDER = "section.admin.invalid_order"

    FILES_TITLE = "files.title"
    FILES_EMPTY = "files.empty"
    FILES_BTN_UPLOAD = "files.btn.upload"
    FILES_BTN_DELETE = "files.btn.delete"
    FILES_BTN_CONFIRM_DELETE = "files.btn.confirm_delete"
    FILES_BTN_CANCEL = "files.btn.cancel"
    FILES_BTN_LINK = "files.btn.link"
    FILES_BTN_UNLINK = "files.btn.unlink"
    FILES_BTN_DONE = "files.btn.done"
    FILES_UPLOAD_PROMPT = "files.upload.prompt"
    FILES_UPLOAD_SUCCESS = "files.upload.success"
    FILES_UPLOAD_COUNT = "files.upload.count"
    FILES_UPLOAD_DUPLICATE = "files.upload.duplicate"
    FILES_UPLOAD_ERROR = "files.upload.error"
    FILES_DELETE_CONFIRM = "files.delete.confirm"
    FILES_DELETED = "files.deleted"
    FILES_NOT_FOUND = "files.not_found"
    FILES_SENT = "files.sent"
    FILES_LINKED = "files.linked"
    FILES_UNLINKED = "files.unlinked"
    FILES_ALREADY_LINKED = "files.already_linked"
    FILES_CANCELLED = "files.cancelled"
    FILES_STORAGE_NOT_SET = "files.storage_not_set"
    FILES_PAGE_INFO = "files.page_info"
    FILES_PAGE_PREV = "files.page_prev"
    FILES_PAGE_NEXT = "files.page_next"
    FILES_DEEP_LINK_NOT_FOUND = "files.deep_link.not_found"


class DefaultTexts:
    TEXTS = {
        "error.general": "حدث خطأ غير متوقع. يرجى المحاولة لاحقاً.",
        "error.blocked": "تم حظرك من استخدام البوت.",
        "error.subscription_required": "يجب الاشتراك في القناة أولاً للاستمرار.",
        "error.permission_denied": "ليس لديك صلاحية للقيام بهذا الإجراء.",
        "error.state_expired": "انتهت مهلة العملية. يرجى المحاولة مرة أخرى.",
        "login.notification": "تسجيل دخول جديد:\nالمعرف: {user_id}\nالاسم: {name}\nالوقت: {time}\nاسم المستخدم: {username}",
        "home.welcome": "مرحباً {name}!\nاختر من القائمة:",
        "home.btn.sections": "📚 الأقسام",
        "home.btn.search": "🔍 البحث",
        "home.btn.contribute": "📤 مساهمة بملف",
        "home.btn.about": "ℹ️ عن البوت",
        "home.btn.contact": "📞 تواصل مع المطور",
        "home.btn.tools": "🧰 أدوات المستخدم",
        "home.btn.back": "رجوع",
        "home.about.text": "بوت المكتبة التعليمية الجامعية\nيتيح لك تصفح الأقسام والملفات والمساهمة بالمحتوى.",
        "home.contact.text": "للتواصل مع المطور يرجى مراسلة الحساب التالي.",
        "home.placeholder": "هذه الميزة قيد التطوير وستكون متاحة قريباً.",
        "home.unknown_text": "لم أفهم رسالتك. يرجى استخدام الأزرار أدناه.",
        "home.btn.admin_panel": "لوحة التحكم",
        "admin.panel.text": "لوحة التحكم الإدارية\nاختر من الخيارات أدناه:",
        "sections.title": "الأقسام المتاحة:",
        "sections.empty": "لا توجد أقسام حالياً.",
        "sections.btn.back": "رجوع",
        "sections.btn.home": "القائمة الرئيسية",
        "section.admin.btn.add": "إضافة قسم",
        "section.admin.btn.edit": "تعديل",
        "section.admin.btn.delete": "حذف",
        "section.admin.btn.order": "ترتيب",
        "section.admin.enter_name": "أدخل اسم القسم الجديد:",
        "section.admin.enter_desc": "أدخل وصف القسم (أو اضغط تخطي):",
        "section.admin.btn.skip_desc": "تخطي الوصف",
        "section.admin.enter_order": "أدخل رقم الترتيب (رقم صحيح):",
        "section.admin.saved": "تم إنشاء القسم بنجاح.",
        "section.admin.updated": "تم تحديث القسم بنجاح.",
        "section.admin.deleted": "تم حذف القسم بنجاح.",
        "section.admin.confirm_delete": "هل أنت متأكد من حذف القسم «{name}»؟",
        "section.admin.btn.confirm": "تأكيد الحذف",
        "section.admin.btn.cancel": "إلغاء",
        "section.admin.cancelled": "تم إلغاء العملية.",
        "section.admin.not_found": "القسم غير موجود.",
        "section.admin.has_children": "لا يمكن حذف القسم لأنه يحتوي على أقسام فرعية.",
        "section.admin.enter_new_name": "أدخل الاسم الجديد للقسم:",
        "section.admin.invalid_order": "يرجى إدخال رقم صحيح للترتيب.",
        "files.title": "الملفات المتاحة:",
        "files.empty": "لا توجد ملفات في هذا القسم.",
        "files.btn.upload": "رفع ملف",
        "files.btn.delete": "حذف الملف",
        "files.btn.confirm_delete": "تأكيد حذف الملف",
        "files.btn.cancel": "إلغاء",
        "files.btn.link": "ربط بقسم آخر",
        "files.btn.unlink": "فك الربط",
        "files.btn.done": "تم الانتهاء",
        "files.upload.prompt": "أرسل الملف أو الملفات المراد رفعها.\nيمكنك إرسال عدة ملفات دفعة واحدة.\nاضغط «تم» عند الانتهاء.",
        "files.upload.success": "تم رفع الملف بنجاح: {name}",
        "files.upload.count": "تم رفع {count} ملف بنجاح.",
        "files.upload.duplicate": "هذا الملف موجود مسبقاً وتم ربطه بالقسم.",
        "files.upload.error": "حدث خطأ أثناء رفع الملف.",
        "files.delete.confirm": "هل أنت متأكد من حذف الملف «{name}»؟",
        "files.deleted": "تم حذف الملف بنجاح.",
        "files.not_found": "الملف غير موجود.",
        "files.sent": "تم إرسال الملف.",
        "files.linked": "تم ربط الملف بالقسم بنجاح.",
        "files.unlinked": "تم فك ربط الملف من القسم.",
        "files.already_linked": "الملف مربوط بهذا القسم مسبقاً.",
        "files.cancelled": "تم إلغاء العملية.",
        "files.storage_not_set": "قناة التخزين غير مُعدة. تواصل مع المسؤول.",
        "files.page_info": "صفحة {page} من {total}",
        "files.page_prev": "السابق",
        "files.page_next": "التالي",
        "files.deep_link.not_found": "الملف المطلوب غير موجود أو تم حذفه.",
    }
