import os

BOT_TOKEN = os.getenv("BOT_TOKEN", "توکن_واقعی_اینجا")
MAIN_ADMINS = [int(x.strip()) for x in os.getenv("MAIN_ADMINS", "7307516760").split(",") if x.strip()]
DB_PATH = os.getenv("DB_PATH", "silaber_pv.db")
PORT = int(os.getenv("PORT", "8080"))

DEFAULTS = {
    "bot_enabled": "1",
    "welcome_text": "👋 سلام!\nبه ربات پیام‌رسان خوش آمدید.",
    "auto_reply_text": "✅ پیامت رسید، آنلاین بشم جواب میدم.",
    "ban_text": "⛔ شما از استفاده از ربات محروم شده‌اید.",
    "force_join_text": "⚠️ برای استفاده از ربات، ابتدا در کانال‌های زیر عضو شوید:",
    "admin_new_msg_text": '📩 پیام جدید از <a href="tg://user?id={user_id}">{user_name}</a> (ID: <code>{user_id}</code>):',
    "panel_type_user": "inline",
    "panel_type_admin": "inline",
    "antispam_enabled": "0",
    "antispam_interval": "3",
    "antispam_limit": "10",
    "antispam_period": "60",
    "antispam_action": "mute",
    "antispam_duration": "3600",
    "anon_enabled": "1",
    "inactive_link_text": "⛔ این لینک ناشناس غیرفعال شده است.",
    "backup_enabled": "0",
    "backup_interval": "3600",
    "backup_channel": "0",
}

MAX_BROADCAST_BATCH = 20
THROTTLE_RATE = 0.5
