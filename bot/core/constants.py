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
    SECTION_TOGGLED = "Section toggled: id={section_id} is_active={is_active}"
    SECTION_COPIED = "Section copied: source={source_id} new={new_id} by user {user_id}"

    FILE_CREATED = "File created: id={file_id} name={name} by user {user_id}"
    FILE_DUPLICATE = "Duplicate file detected: unique_id={file_unique_id}"
    FILE_LINKED = "File {file_id} linked to section {section_id}"
    FILE_UNLINKED = "File {file_id} unlinked from section {section_id}"
    FILE_SENT = "File {file_id} sent to user {user_id}"
    FILE_FORWARDED = "File forwarded to storage channel: {file_id}"
    FILE_SOFT_DELETED = "File soft deleted: id={file_id} name={name}"
    FILE_SEND_FAILED = "Failed to send file {file_id}: {error}"
    FILE_STATUS_CHANGED = "File {file_id} status changed to {status} by user {user_id}"
    MEDIA_GROUP_RECEIVED = "Media group received: {count} files from user {user_id}"
    DEEP_LINK = "Deep link: user {user_id} requested file {file_id}"
    STORAGE_CHANNEL_NOT_SET = "STORAGE_CHANNEL_ID not set - file storage disabled"

    SEARCH_STARTED = "Search started by user {user_id}"
    SEARCH_QUERY = "Search query from user {user_id}: {query}"
    SEARCH_RESULTS = "Search results for user {user_id}: {sections} sections, {files} files"
    SEARCH_RESULT_SELECTED = "Search result selected by user {user_id}: {type} {id}"

    MODERATOR_ADDED = "Moderator added: user {target_id} by admin {admin_id}"
    MODERATOR_REMOVED = "Moderator removed: user {target_id} by admin {admin_id}"
    MODERATOR_PERMS_UPDATED = "Moderator permissions updated: user {target_id} by admin {admin_id}"

    TEXT_UPDATED = "Text updated: key={key} by admin {admin_id}"

    CONTRIBUTION_APPROVED = "Contribution approved: file {file_id} by admin {admin_id}"
    CONTRIBUTION_REJECTED = "Contribution rejected: file {file_id} by admin {admin_id}"


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
    SECTION_TOGGLED = "section_toggled"
    SECTION_COPIED = "section_copied"
    FILE_UPLOADED = "file_uploaded"
    FILE_DELETED = "file_deleted"
    FILE_LINKED = "file_linked"
    FILE_UNLINKED = "file_unlinked"
    FILE_STATUS_CHANGED = "file_status_changed"
    MODERATOR_ADDED = "moderator_added"
    MODERATOR_REMOVED = "moderator_removed"
    MODERATOR_PERMS_UPDATED = "moderator_perms_updated"
    TEXT_UPDATED = "text_updated"
    CONTRIBUTION_APPROVED = "contribution_approved"
    CONTRIBUTION_REJECTED = "contribution_rejected"


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
    SECTION_ADMIN_TOGGLE = "sec_tog:"
    SECTION_ADMIN_COPY = "sec_copy:"
    SECTION_ADMIN_CONFIRM_COPY = "sec_ccopy:"
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
    SEARCH_RESULT_SECTION = "sr_sec:"
    SEARCH_RESULT_FILE = "sr_file:"
    SEARCH_BACK = "sr_back"
    CONTRIBUTE = "contribute"
    ABOUT = "about"
    CONTACT = "contact"
    TOOLS = "tools"
    BACK = "back"
    ADMIN_PANEL = "admin_panel"
    ADMIN_SECTIONS = "adm_sec"
    ADMIN_FILES = "adm_files"
    ADMIN_FILES_PAGE = "adm_fp:"
    ADMIN_FILE_DETAIL = "adm_fd:"
    ADMIN_FILE_TOGGLE_STATUS = "adm_fts:"
    ADMIN_FILE_LINK_PICK = "adm_flp:"
    ADMIN_FILE_LINK_SEC = "adm_fls:"
    ADMIN_FILE_UNLINK_PICK = "adm_fulp:"
    ADMIN_FILE_UNLINK_SEC = "adm_fuls:"
    ADMIN_MODERATORS = "adm_mods"
    ADMIN_MOD_VIEW = "adm_mv:"
    ADMIN_MOD_ADD = "adm_ma"
    ADMIN_MOD_REMOVE = "adm_mr:"
    ADMIN_MOD_CONFIRM_REMOVE = "adm_mcr:"
    ADMIN_MOD_PERMS = "adm_mp:"
    ADMIN_MOD_TOGGLE_PERM = "adm_mtp:"
    ADMIN_TEXTS = "adm_texts"
    ADMIN_TEXT_EDIT = "adm_te:"
    ADMIN_CONTRIBUTIONS = "adm_contrib"
    ADMIN_CONTRIB_PAGE = "adm_cp:"
    ADMIN_CONTRIB_VIEW = "adm_cv:"
    ADMIN_CONTRIB_APPROVE = "adm_ca:"
    ADMIN_CONTRIB_REJECT = "adm_cr:"
    ADMIN_AUDIT = "adm_audit"
    ADMIN_AUDIT_PAGE = "adm_ap:"
    ADMIN_BACK = "adm_back"


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
    ADMIN_BTN_SECTIONS = "admin.btn.sections"
    ADMIN_BTN_FILES = "admin.btn.files"
    ADMIN_BTN_MODERATORS = "admin.btn.moderators"
    ADMIN_BTN_TEXTS = "admin.btn.texts"
    ADMIN_BTN_CONTRIBUTIONS = "admin.btn.contributions"
    ADMIN_BTN_AUDIT = "admin.btn.audit"
    ADMIN_BTN_BACK = "admin.btn.back"

    SECTIONS_TITLE = "sections.title"
    SECTIONS_EMPTY = "sections.empty"
    SECTIONS_BTN_BACK = "sections.btn.back"
    SECTIONS_BTN_HOME = "sections.btn.home"

    SECTION_ADMIN_BTN_ADD = "section.admin.btn.add"
    SECTION_ADMIN_BTN_EDIT = "section.admin.btn.edit"
    SECTION_ADMIN_BTN_DELETE = "section.admin.btn.delete"
    SECTION_ADMIN_BTN_ORDER = "section.admin.btn.order"
    SECTION_ADMIN_BTN_TOGGLE_HIDE = "section.admin.btn.toggle_hide"
    SECTION_ADMIN_BTN_TOGGLE_SHOW = "section.admin.btn.toggle_show"
    SECTION_ADMIN_BTN_COPY = "section.admin.btn.copy"
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
    SECTION_ADMIN_TOGGLED_HIDDEN = "section.admin.toggled_hidden"
    SECTION_ADMIN_TOGGLED_SHOWN = "section.admin.toggled_shown"
    SECTION_ADMIN_CONFIRM_COPY = "section.admin.confirm_copy"
    SECTION_ADMIN_COPIED = "section.admin.copied"

    FILES_TITLE = "files.title"
    FILES_BTN_VIEW = "files.btn.view"
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

    SEARCH_PROMPT = "search.prompt"
    SEARCH_RESULTS_TITLE = "search.results_title"
    SEARCH_NO_RESULTS = "search.no_results"
    SEARCH_RESULT_SECTION_LABEL = "search.result.section"
    SEARCH_RESULT_FILE_LABEL = "search.result.file"
    SEARCH_BTN_BACK = "search.btn.back"
    SEARCH_QUERY_TOO_SHORT = "search.query_too_short"

    ADMIN_FILES_TITLE = "admin.files.title"
    ADMIN_FILES_EMPTY = "admin.files.empty"
    ADMIN_FILE_DETAIL_TEXT = "admin.file.detail"
    ADMIN_FILE_BTN_PUBLISH = "admin.file.btn.publish"
    ADMIN_FILE_BTN_DRAFT = "admin.file.btn.draft"
    ADMIN_FILE_BTN_LINK = "admin.file.btn.link"
    ADMIN_FILE_BTN_UNLINK = "admin.file.btn.unlink"
    ADMIN_FILE_STATUS_CHANGED = "admin.file.status_changed"
    ADMIN_FILE_SELECT_SECTION_LINK = "admin.file.select_section_link"
    ADMIN_FILE_SELECT_SECTION_UNLINK = "admin.file.select_section_unlink"
    ADMIN_FILE_LINKED = "admin.file.linked"
    ADMIN_FILE_UNLINKED = "admin.file.unlinked"
    ADMIN_FILE_NO_SECTIONS = "admin.file.no_sections"

    ADMIN_MODS_TITLE = "admin.mods.title"
    ADMIN_MODS_EMPTY = "admin.mods.empty"
    ADMIN_MOD_BTN_ADD = "admin.mod.btn.add"
    ADMIN_MOD_ENTER_ID = "admin.mod.enter_id"
    ADMIN_MOD_ADDED = "admin.mod.added"
    ADMIN_MOD_NOT_FOUND = "admin.mod.not_found"
    ADMIN_MOD_ALREADY_MOD = "admin.mod.already_mod"
    ADMIN_MOD_INVALID_ID = "admin.mod.invalid_id"
    ADMIN_MOD_DETAIL = "admin.mod.detail"
    ADMIN_MOD_BTN_REMOVE = "admin.mod.btn.remove"
    ADMIN_MOD_BTN_PERMS = "admin.mod.btn.perms"
    ADMIN_MOD_CONFIRM_REMOVE = "admin.mod.confirm_remove"
    ADMIN_MOD_REMOVED = "admin.mod.removed"
    ADMIN_MOD_PERMS_TITLE = "admin.mod.perms.title"
    ADMIN_MOD_PERMS_UPDATED = "admin.mod.perms.updated"
    ADMIN_MOD_PERM_UPLOAD = "admin.mod.perm.upload"
    ADMIN_MOD_PERM_LINK = "admin.mod.perm.link"
    ADMIN_MOD_PERM_PUBLISH = "admin.mod.perm.publish"
    ADMIN_MOD_PERM_OWN_ONLY = "admin.mod.perm.own_only"
    ADMIN_MOD_CANNOT_ADD_SELF = "admin.mod.cannot_add_self"

    ADMIN_TEXTS_TITLE = "admin.texts.title"
    ADMIN_TEXT_CURRENT = "admin.text.current"
    ADMIN_TEXT_ENTER_NEW = "admin.text.enter_new"
    ADMIN_TEXT_UPDATED = "admin.text.updated"

    ADMIN_CONTRIB_TITLE = "admin.contrib.title"
    ADMIN_CONTRIB_EMPTY = "admin.contrib.empty"
    ADMIN_CONTRIB_DETAIL = "admin.contrib.detail"
    ADMIN_CONTRIB_BTN_APPROVE = "admin.contrib.btn.approve"
    ADMIN_CONTRIB_BTN_REJECT = "admin.contrib.btn.reject"
    ADMIN_CONTRIB_APPROVED = "admin.contrib.approved"
    ADMIN_CONTRIB_REJECTED = "admin.contrib.rejected"
    ADMIN_CONTRIB_USER_APPROVED = "admin.contrib.user_approved"
    ADMIN_CONTRIB_USER_REJECTED = "admin.contrib.user_rejected"

    ADMIN_AUDIT_TITLE = "admin.audit.title"
    ADMIN_AUDIT_EMPTY = "admin.audit.empty"
    ADMIN_AUDIT_ENTRY = "admin.audit.entry"

    CONTRIBUTE_PROMPT = "contribute.prompt"
    CONTRIBUTE_SUCCESS = "contribute.success"
    CONTRIBUTE_DUPLICATE = "contribute.duplicate"


class DefaultTexts:
    TEXTS = {
        "error.general": "⚠️ حدث خطأ غير متوقع. يرجى المحاولة لاحقاً.",
        "error.blocked": "🚫 تم حظرك من استخدام البوت.",
        "error.subscription_required": "📢 يجب الاشتراك في القناة أولاً للاستمرار.",
        "error.permission_denied": "🔒 ليس لديك صلاحية للقيام بهذا الإجراء.",
        "error.state_expired": "⏱ انتهت مهلة العملية. يرجى المحاولة مرة أخرى.",
        "login.notification": "تسجيل دخول جديد:\nالمعرف: {user_id}\nالاسم: {name}\nالوقت: {time}\nاسم المستخدم: {username}",
        "home.welcome": "👋 مرحباً <b>{name}</b>!\n\n📖 اختر من القائمة أدناه:",
        "home.btn.sections": "📚 الأقسام",
        "home.btn.search": "🔍 البحث",
        "home.btn.contribute": "📤 مساهمة بملف",
        "home.btn.about": "ℹ️ عن البوت",
        "home.btn.contact": "📞 تواصل مع المطور",
        "home.btn.tools": "🧰 أدوات المستخدم",
        "home.btn.back": "🔙 رجوع",
        "home.about.text": "📖 <b>بوت المكتبة التعليمية الجامعية</b>\n\nيتيح لك تصفح الأقسام والملفات والمساهمة بالمحتوى التعليمي.",
        "home.contact.text": "📬 <b>تواصل مع المطور</b>\n\nللتواصل مع المطور يرجى مراسلة الحساب التالي.",
        "home.placeholder": "🔧 هذه الميزة قيد التطوير وستكون متاحة قريباً.",
        "home.unknown_text": "❓ لم أفهم رسالتك. يرجى استخدام الأزرار أدناه.",
        "home.btn.admin_panel": "⚙️ لوحة التحكم",
        "admin.panel.text": "⚙️ <b>لوحة التحكم الإدارية</b>\n\nاختر من الخيارات أدناه لإدارة البوت:",
        "admin.btn.sections": "📂 إدارة الأقسام",
        "admin.btn.files": "📄 إدارة الملفات",
        "admin.btn.moderators": "👥 إدارة المشرفين",
        "admin.btn.texts": "📝 إدارة النصوص",
        "admin.btn.contributions": "📥 مراجعة المساهمات",
        "admin.btn.audit": "📋 سجل العمليات",
        "admin.btn.back": "🔙 رجوع للوحة التحكم",
        "sections.title": "📚 <b>الأقسام المتاحة</b>",
        "sections.empty": "📭 لا توجد أقسام حالياً.",
        "sections.btn.back": "🔙 رجوع",
        "sections.btn.home": "🏠 القائمة الرئيسية",
        "section.admin.btn.add": "➕ إضافة قسم",
        "section.admin.btn.edit": "✏️ تعديل",
        "section.admin.btn.delete": "🗑 حذف",
        "section.admin.btn.order": "🔢 ترتيب",
        "section.admin.btn.toggle_hide": "🙈 إخفاء القسم",
        "section.admin.btn.toggle_show": "👁 إظهار القسم",
        "section.admin.btn.copy": "📋 نسخ القسم",
        "section.admin.enter_name": "✏️ أدخل اسم القسم الجديد:",
        "section.admin.enter_desc": "📝 أدخل وصف القسم (أو اضغط تخطي):",
        "section.admin.btn.skip_desc": "⏭ تخطي الوصف",
        "section.admin.enter_order": "🔢 أدخل رقم الترتيب (رقم صحيح):",
        "section.admin.saved": "✅ تم إنشاء القسم بنجاح.",
        "section.admin.updated": "✅ تم تحديث القسم بنجاح.",
        "section.admin.deleted": "🗑 تم حذف القسم بنجاح.",
        "section.admin.confirm_delete": "⚠️ هل أنت متأكد من حذف القسم «{name}»؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
        "section.admin.btn.confirm": "🗑 تأكيد الحذف",
        "section.admin.btn.cancel": "❌ إلغاء",
        "section.admin.cancelled": "تم إلغاء العملية.",
        "section.admin.not_found": "⚠️ القسم غير موجود.",
        "section.admin.has_children": "⚠️ لا يمكن حذف القسم لأنه يحتوي على أقسام فرعية.",
        "section.admin.enter_new_name": "✏️ أدخل الاسم الجديد للقسم:",
        "section.admin.invalid_order": "⚠️ يرجى إدخال رقم صحيح للترتيب.",
        "section.admin.toggled_hidden": "🙈 تم إخفاء القسم «{name}» بنجاح.",
        "section.admin.toggled_shown": "👁 تم إظهار القسم «{name}» بنجاح.",
        "section.admin.confirm_copy": "📋 هل تريد نسخ القسم «{name}» مع جميع أقسامه الفرعية وروابط الملفات؟",
        "section.admin.copied": "✅ تم نسخ القسم بنجاح. القسم الجديد: «{name}»",
        "files.title": "📄 <b>الملفات المتاحة</b>",
        "files.btn.view": "📄 الملفات",
        "files.empty": "📭 لا توجد ملفات في هذا القسم.",
        "files.btn.upload": "📤 رفع ملف",
        "files.btn.delete": "🗑 حذف الملف",
        "files.btn.confirm_delete": "🗑 تأكيد حذف الملف",
        "files.btn.cancel": "❌ إلغاء",
        "files.btn.link": "🔗 ربط بقسم آخر",
        "files.btn.unlink": "✂️ فك الربط",
        "files.btn.done": "✅ تم الانتهاء",
        "files.upload.prompt": "📤 <b>رفع ملفات</b>\n\nأرسل الملف أو الملفات المراد رفعها.\nيمكنك إرسال عدة ملفات دفعة واحدة.\n\nاضغط «✅ تم» عند الانتهاء.",
        "files.upload.success": "✅ تم رفع الملف: {name}",
        "files.upload.count": "✅ تم رفع {count} ملف بنجاح.",
        "files.upload.duplicate": "🔄 هذا الملف موجود مسبقاً وتم ربطه بالقسم.",
        "files.upload.error": "⚠️ حدث خطأ أثناء رفع الملف.",
        "files.delete.confirm": "⚠️ هل أنت متأكد من حذف الملف «{name}»؟\n\nهذا الإجراء لا يمكن التراجع عنه.",
        "files.deleted": "🗑 تم حذف الملف بنجاح.",
        "files.not_found": "⚠️ الملف غير موجود.",
        "files.sent": "تم إرسال الملف.",
        "files.linked": "✅ تم ربط الملف بالقسم بنجاح.",
        "files.unlinked": "✅ تم فك ربط الملف من القسم.",
        "files.already_linked": "🔄 الملف مربوط بهذا القسم مسبقاً.",
        "files.cancelled": "تم إلغاء العملية.",
        "files.storage_not_set": "⚠️ قناة التخزين غير مُعدة. تواصل مع المسؤول.",
        "files.page_info": "📄 {page} / {total}",
        "files.page_prev": "◀️ السابق",
        "files.page_next": "التالي ▶️",
        "files.deep_link.not_found": "⚠️ الملف المطلوب غير موجود أو تم حذفه.",
        "search.prompt": "🔍 <b>البحث</b>\n\nأدخل نص البحث للبحث في الأقسام والملفات:",
        "search.results_title": "🔍 <b>نتائج البحث عن:</b> «{query}»\n\n{count} نتيجة",
        "search.no_results": "🔍 لا توجد نتائج مطابقة.",
        "search.result.section": "📁 {name}",
        "search.result.file": "📄 {name}",
        "search.btn.back": "🔙 رجوع من البحث",
        "search.query_too_short": "⚠️ يرجى إدخال حرفين على الأقل للبحث.",
        "admin.files.title": "📄 <b>إدارة الملفات</b>\n\nجميع الملفات ({count}):",
        "admin.files.empty": "📭 لا توجد ملفات في النظام.",
        "admin.file.detail": "📄 <b>{name}</b>\n\nالنوع: {file_type}\nالحالة: {status}\nرفع بواسطة: {uploaded_by}\nالأقسام: {sections}",
        "admin.file.btn.publish": "✅ نشر",
        "admin.file.btn.draft": "📝 مسودة",
        "admin.file.btn.link": "🔗 ربط بقسم",
        "admin.file.btn.unlink": "✂️ فك ربط من قسم",
        "admin.file.status_changed": "✅ تم تغيير حالة الملف إلى: {status}",
        "admin.file.select_section_link": "🔗 اختر القسم لربط الملف به:",
        "admin.file.select_section_unlink": "✂️ اختر القسم لفك ربط الملف منه:",
        "admin.file.linked": "✅ تم ربط الملف بالقسم بنجاح.",
        "admin.file.unlinked": "✅ تم فك ربط الملف من القسم بنجاح.",
        "admin.file.no_sections": "📭 لا توجد أقسام متاحة.",
        "admin.mods.title": "👥 <b>إدارة المشرفين</b>\n\nالمشرفون الحاليون:",
        "admin.mods.empty": "📭 لا يوجد مشرفون حالياً.",
        "admin.mod.btn.add": "➕ إضافة مشرف",
        "admin.mod.enter_id": "👤 أدخل معرف المستخدم (Telegram ID) لإضافته كمشرف:",
        "admin.mod.added": "✅ تم إضافة المشرف بنجاح: {name}",
        "admin.mod.not_found": "⚠️ المستخدم غير موجود. يجب أن يكون قد استخدم البوت مسبقاً.",
        "admin.mod.already_mod": "⚠️ هذا المستخدم مشرف بالفعل.",
        "admin.mod.invalid_id": "⚠️ يرجى إدخال معرف رقمي صحيح.",
        "admin.mod.detail": "👤 <b>المشرف:</b> {name}\n\nالمعرف: <code>{user_id}</code>\nاسم المستخدم: {username}\n\nالصلاحيات:\n{permissions}",
        "admin.mod.btn.remove": "🗑 إزالة المشرف",
        "admin.mod.btn.perms": "⚙️ تعديل الصلاحيات",
        "admin.mod.confirm_remove": "⚠️ هل أنت متأكد من إزالة «{name}» من المشرفين؟",
        "admin.mod.removed": "✅ تم إزالة المشرف بنجاح.",
        "admin.mod.perms.title": "⚙️ <b>صلاحيات المشرف:</b> {name}\n\nاضغط على الصلاحية لتفعيلها/تعطيلها:",
        "admin.mod.perms.updated": "✅ تم تحديث الصلاحيات بنجاح.",
        "admin.mod.perm.upload": "📤 رفع ملفات",
        "admin.mod.perm.link": "🔗 ربط ملفات بأقسام",
        "admin.mod.perm.publish": "✅ نشر / إخفاء ملفات",
        "admin.mod.perm.own_only": "🔒 إدارة ملفاته فقط",
        "admin.mod.cannot_add_self": "⚠️ لا يمكنك إضافة نفسك كمشرف.",
        "admin.texts.title": "📝 <b>إدارة النصوص</b>\n\nاختر النص المراد تعديله:",
        "admin.text.current": "📝 <b>النص الحالي لـ «{label}»:</b>\n\n{text}\n\nأرسل النص الجديد:",
        "admin.text.enter_new": "📝 أرسل النص الجديد:",
        "admin.text.updated": "✅ تم تحديث النص بنجاح.",
        "admin.contrib.title": "📥 <b>مراجعة المساهمات</b>\n\nالمساهمات المعلقة ({count}):",
        "admin.contrib.empty": "📭 لا توجد مساهمات معلقة.",
        "admin.contrib.detail": "📄 <b>{name}</b>\n\nالنوع: {file_type}\nمن المستخدم: {user_name} (<code>{user_id}</code>)",
        "admin.contrib.btn.approve": "✅ قبول",
        "admin.contrib.btn.reject": "❌ رفض",
        "admin.contrib.approved": "✅ تم قبول المساهمة ونشر الملف.",
        "admin.contrib.rejected": "❌ تم رفض المساهمة.",
        "admin.contrib.user_approved": "🎉 تم قبول مساهمتك «{name}» ونشرها في المكتبة!",
        "admin.contrib.user_rejected": "❌ تم رفض مساهمتك «{name}».",
        "admin.audit.title": "📋 <b>سجل العمليات</b>\n\nآخر العمليات:",
        "admin.audit.empty": "📭 لا توجد عمليات مسجلة.",
        "admin.audit.entry": "👤 {user_id} | {action}\n📅 {time}\n{details}",
        "contribute.prompt": "📤 <b>مساهمة بملف</b>\n\nأرسل الملف المراد المساهمة به.\nسيتم مراجعته من قبل الإدارة قبل النشر.\n\nاضغط «🔙 رجوع» للعودة.",
        "contribute.success": "✅ تم استلام مساهمتك بنجاح!\nسيتم مراجعتها من قبل الإدارة.",
        "contribute.duplicate": "🔄 هذا الملف تم إرساله مسبقاً.",
    }
