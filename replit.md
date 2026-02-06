# بوت المكتبة التعليمية الجامعية

## نظرة عامة
بوت تيليجرام لإدارة مكتبة تعليمية جامعية، يتيح للمستخدمين تصفح الأقسام والملفات والمساهمة بالمحتوى.

## التقنيات المستخدمة
- **Python 3.11**
- **aiogram** - إطار عمل بوت تيليجرام
- **SQLAlchemy** - ORM لقاعدة البيانات
- **asyncpg** - مشغل PostgreSQL غير متزامن
- **Alembic** - إدارة الهجرات

## هيكل المشروع
```
bot/
├── core/                    # النواة الأساسية
│   ├── config.py            # إعدادات التطبيق
│   ├── constants.py         # الثوابت المركزية (LogMessages, ErrorMessages, I18nKeys, DefaultTexts, AuditActions, CallbackPrefixes)
│   ├── database.py          # اتصال قاعدة البيانات
│   └── logging_config.py    # إعدادات التسجيل
├── handlers/                # معالجات الرسائل والأوامر
│   ├── home.py              # واجهة المستخدم الرئيسية + أزرار التنقل + لوحة التحكم + deep linking
│   ├── sections.py          # عرض الأقسام + إدارة الأقسام (admin FSM)
│   ├── files.py             # رفع/عرض/حذف الملفات + FSM + pagination + deep linking
│   └── fallback.py          # معالج الرسائل النصية غير المعروفة
├── middlewares/             # الوسطاء
│   ├── ban_check.py         # فحص الحظر
│   ├── subscription_check.py # فحص الاشتراك الإجباري
│   ├── role_check.py        # فحص الدور وتحميله في data["user_role"]
│   ├── user_tracking.py     # تتبع المستخدمين
│   └── i18n_middleware.py   # حقن خدمة النصوص
├── models/                  # نماذج قاعدة البيانات
│   ├── user.py              # نموذج المستخدم (User, UserRole)
│   ├── text_entry.py        # نموذج النصوص الديناميكية
│   ├── setting.py           # نموذج الإعدادات
│   ├── audit_log.py         # نموذج سجل الإجراءات (AuditLog)
│   ├── section.py           # نموذج القسم (Section)
│   ├── file.py              # نموذج الملف (File, FileType, FileStatus)
│   └── file_section.py      # جدول الربط ملف-قسم (many-to-many)
├── modules/                 # وحدات البوت
│   ├── central_router.py    # التوجيه المركزي للأزرار
│   ├── error_handler.py     # معالج الأخطاء العام
│   ├── health_check.py      # فحص جاهزية النظام
│   └── login_logger.py      # تسجيل دخول المستخدمين
├── services/                # طبقة الخدمات
│   ├── i18n.py              # خدمة النصوص الديناميكية
│   ├── state.py             # إدارة الحالات
│   ├── user.py              # خدمة المستخدمين
│   ├── seeder.py            # زراعة النصوص الافتراضية
│   ├── permissions.py       # نظام الصلاحيات المركزي (Permission, ROLE_PERMISSIONS)
│   ├── audit.py             # خدمة سجل الإجراءات
│   ├── sections.py          # خدمة الأقسام (CRUD + ترتيب + تداخل)
│   └── files.py             # خدمة الملفات (CRUD + ربط بالأقسام + كشف التكرار)
├── utils/                   # أدوات مساعدة
├── migrations/              # هجرات Alembic
│   ├── env.py
│   ├── script.py.mako
│   └── versions/            # ملفات الهجرات
└── main.py                  # نقطة التشغيل
```

## المتغيرات البيئية
| المتغير | الوصف |
|---------|-------|
| `BOT_TOKEN` | توكن البوت من BotFather |
| `DATABASE_URL` | رابط اتصال PostgreSQL |
| `DEBUG` | وضع التصحيح (true/false) |
| `LOG_CHANNEL_ID` | معرف قناة المراقبة (0 = معطل) |
| `SUBSCRIPTION_ENABLED` | تفعيل الاشتراك الإجباري (true/false) |
| `SUBSCRIPTION_CHANNEL_IDS` | معرفات القنوات المطلوبة (مفصولة بفواصل) |
| `STATE_TIMEOUT_SECONDS` | مهلة انتهاء الحالة بالثواني (افتراضي: 300) |
| `STORAGE_CHANNEL_ID` | معرف قناة التخزين للملفات (0 = معطل) |
| `DEFAULT_LANGUAGE` | اللغة الافتراضية (افتراضي: ar) |

## جداول قاعدة البيانات
| الجدول | الوصف |
|--------|-------|
| `users` | بيانات المستخدمين والأدوار والحظر |
| `text_entries` | النصوص الديناميكية (I18n) |
| `settings` | إعدادات النظام |
| `audit_logs` | سجل الإجراءات الإدارية (من، ماذا، متى) |
| `sections` | الأقسام المتداخلة (اسم، وصف، parent_id، ترتيب، حالة) |
| `files` | الملفات (file_id, file_unique_id, name, type, size, status, uploaded_by) |
| `file_sections` | ربط الملفات بالأقسام (many-to-many) |

## نظام الأدوار والصلاحيات
| الدور | الصلاحيات |
|-------|-----------|
| `user` | تصفح الواجهة فقط (browse) |
| `moderator` | تصفح + رفع ملفات (browse, upload_file) |
| `admin` | تحكم كامل (browse, upload_file, manage_sections, manage_files, manage_users, manage_settings, view_audit_log, view_admin_panel) |

### آلية فحص الصلاحيات
- `permissions.py` يحتوي على `Permission` (ثوابت الصلاحيات) و`ROLE_PERMISSIONS` (ربط الأدوار بالصلاحيات)
- `has_permission(role, permission)` للفحص البرمجي
- `check_permission_and_notify(callback, role, permission)` للفحص مع إرسال رسالة رفض
- الأزرار الإدارية تُخفى تلقائياً حسب الدور في `build_home_keyboard(role)`

### سجل الإجراءات (Audit Log)
- `AuditActions` في `constants.py` يحتوي على أنواع الإجراءات
- `audit_service.log_action(session, user_id, action, details)` لتسجيل أي إجراء
- يُستخدم فعلياً في إدارة الأقسام والملفات (إنشاء، تعديل، حذف)

## وحدة الأقسام (المرحلة 4)

### نموذج البيانات
- `Section`: id, name, description, parent_id (FK ذاتي), order, is_active, created_at
- التداخل عبر parent_id (أقسام رئيسية ← أقسام فرعية)
- الحذف منطقي (is_active = False)

### بادئات الأزرار (Callback Prefixes)
| البادئة | الاستخدام |
|---------|-----------|
| `sec:{id}` | عرض قسم (تنقل المستخدم) |
| `sec_back:{id}` | رجوع للقسم الأب (0 = الجذر) |
| `sec_add:{parent_id}` | إضافة قسم (أدمن) |
| `sec_edit:{id}` | تعديل اسم قسم (أدمن) |
| `sec_ord:{id}` | تعديل ترتيب قسم (أدمن) |
| `sec_del:{id}` | حذف قسم (أدمن) |
| `sec_cdel:{id}` | تأكيد حذف قسم (أدمن) |
| `sec_cancel` | إلغاء العملية الإدارية |
| `sec_skip_desc` | تخطي الوصف عند الإضافة |

### حالات FSM للأدمن
| الحالة | الوصف |
|--------|-------|
| `section_add_name` | انتظار اسم القسم الجديد |
| `section_add_desc` | انتظار وصف القسم (اختياري) |
| `section_edit_name` | انتظار الاسم الجديد |
| `section_edit_order` | انتظار رقم الترتيب الجديد |

### تدفق إنشاء قسم
1. أدمن يضغط "إضافة قسم" → state = section_add_name
2. يكتب الاسم → state = section_add_desc
3. يكتب الوصف أو يضغط "تخطي" → يُنشأ القسم + audit log

## وحدة الملفات (المرحلة 5)

### نموذج البيانات
- `File`: id, file_id (telegram), file_unique_id, name, file_type (enum), file_size, status (enum), uploaded_by, is_active, created_at
- `FileSection`: file_id + section_id (جدول ربط many-to-many)
- `FileType`: DOCUMENT, PHOTO, VIDEO, AUDIO, VOICE, VIDEO_NOTE, ANIMATION, STICKER
- `FileStatus`: PENDING, PUBLISHED
- كشف التكرار عبر file_unique_id
- الحذف منطقي (is_active = False)

### بادئات الأزرار (Callback Prefixes)
| البادئة | الاستخدام |
|---------|-----------|
| `file:{id}` | عرض/إرسال ملف |
| `fpage:{section_id}:{page}` | تصفح صفحات الملفات |
| `f_up:{section_id}` | بدء رفع ملفات |
| `f_del:{id}` | حذف ملف |
| `f_cdel:{id}` | تأكيد حذف ملف |
| `f_done` | إنهاء جلسة الرفع |
| `f_cancel` | إلغاء جلسة الرفع |

### حالة FSM للرفع
| الحالة | الوصف |
|--------|-------|
| `file_upload` | انتظار ملفات من المستخدم (section_id, uploaded_count في state_data) |

### تدفق رفع الملفات
1. مشرف/أدمن يضغط "رفع ملفات" في قسم → state = file_upload
2. يرسل ملفات (واحد أو عدة) → كل ملف يُحفظ ويُربط بالقسم
3. يضغط "انتهيت" أو "إلغاء" → ملخص أو إلغاء
4. الملفات تُحول لقناة التخزين (STORAGE_CHANNEL_ID) وfile_id يُحفظ
5. كشف التكرار: إذا وُجد ملف بنفس file_unique_id يُربط بالقسم الحالي بدلاً من إعادة الرفع

### Deep Linking
- رابط مباشر للملف: `t.me/bot?start=file_<id>`
- يُعالج في /start handler ويرسل الملف مباشرة للمستخدم

### التصفح المُقسّم (Pagination)
- 5 ملفات لكل صفحة
- أزرار التنقل (السابق/التالي) مع رقم الصفحة
- أزرار إدارية (رفع/حذف) تظهر حسب الصلاحيات

## أوامر Alembic
```bash
alembic current          # عرض الحالة الحالية
alembic upgrade head     # تطبيق جميع الهجرات
alembic revision -m "x"  # إنشاء هجرة جديدة
alembic downgrade -1     # التراجع عن آخر هجرة
```

## تشغيل البوت
```bash
python -m bot.main
```

## البنية المعمارية
- **النصوص**: جميع النصوص الموجهة للمستخدم في جدول `text_entries` عبر I18nService
- **النصوص الداخلية**: جميع رسائل الـ logging والأخطاء في `constants.py`
- **الوسطاء**: يُنفذون بالترتيب: حظر → اشتراك → تتبع → دور → I18n
- **CallbackPrefixes**: جميع بادئات الأزرار في `constants.py`
- **الحالات**: حالة واحدة لكل مستخدم مع مهلة زمنية قابلة للتكوين
- **التوجيه المركزي**: جميع callbacks تمر عبر CentralRouter
- **الصلاحيات**: فحص مركزي عبر `permissions.py` قبل أي إجراء إداري
- **سجل الإجراءات**: تسجيل كل إجراء إداري في `audit_logs`
- **ترتيب الراوترات**: home → files → sections → central → fallback (files قبل sections لالتقاط رسائل FSM)

## المراحل المكتملة
- [x] المرحلة 0: التهيئة
- [x] المرحلة 1: النواة + النصوص الديناميكية
- [x] المرحلة 2: واجهة المستخدم الرئيسية
- [x] المرحلة 3: وحدة الصلاحيات
- [x] المرحلة 4: وحدة الأقسام
- [x] المرحلة 5: وحدة الملفات

## المراحل القادمة
- [ ] المرحلة 6: البحث
- [ ] المرحلة 7: لوحة الأدمن
- [ ] المرحلة 8: وحدة المساهمات
- [ ] المرحلة 9: المهام الثقيلة
- [ ] المرحلة 10: المساعد الذكي
