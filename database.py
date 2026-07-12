import aiosqlite
import datetime
from config import DB_PATH, DEFAULTS, MAIN_ADMINS

DEFAULT_USER_BUTTONS = [
    ("user_links", "🔗 لینک ناشناس من", "my_links", 0, 0),
    ("user_send_admin", "📨 ارسال پیام به ادمین", "send_anon_to_admin", 0, 1),
    ("user_tools", "🔧 ابزارها", "tools_menu", 1, 0),
]

DEFAULT_ADMIN_BUTTONS = [
    ("admin_stats", "📊 آمار و وضعیت", "adm_stats", 0, 0),
    ("admin_admins", "👥 مدیریت ادمین‌ها", "adm_admins", 0, 1),
    ("admin_channels", "📢 مدیریت چنل‌ها", "adm_channels", 1, 0),
    ("admin_texts", "✏️ مدیریت متن‌ها", "adm_texts", 1, 1),
    ("admin_msg", "📨 ارسال پیام", "adm_messaging", 2, 0),
    ("admin_buttons", "🔧 مدیریت دکمه‌ها", "adm_buttons", 2, 1),
    ("admin_antispam", "🛡️ ضد اسپم", "adm_antispam", 3, 0),
    ("admin_anon", "🔒 ناشناس", "adm_anon", 3, 1),
    ("admin_status", "⚙️ وضعیت ربات", "adm_bot_status", 4, 0),
    ("admin_backup", "📁 بکاپ", "adm_backup", 4, 1),
]


async def get_db():
    db = await aiosqlite.connect(DB_PATH)
    db.row_factory = aiosqlite.Row
    await db.execute("PRAGMA journal_mode=WAL")
    await db.execute("PRAGMA synchronous=NORMAL")
    return db


async def init_db():
    db = await get_db()
    try:
        await db.executescript("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY, username TEXT, first_name TEXT,
                join_date TEXT DEFAULT (datetime('now')), last_activity TEXT DEFAULT (datetime('now')),
                is_banned INTEGER DEFAULT 0, total_messages INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS admins (
                user_id INTEGER PRIMARY KEY, username TEXT, added_by INTEGER,
                added_at TEXT DEFAULT (datetime('now')), last_activity TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, from_user_id INTEGER, target_user_id INTEGER,
                content_type TEXT, file_id TEXT, text TEXT, caption TEXT,
                timestamp TEXT DEFAULT (datetime('now')), is_from_admin INTEGER DEFAULT 0, is_anonymous INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS message_mapping (
                bot_message_id INTEGER, chat_id INTEGER, target_user_id INTEGER,
                original_user_id INTEGER, is_anonymous INTEGER DEFAULT 0,
                link_owner_id INTEGER DEFAULT 0, timestamp TEXT DEFAULT (datetime('now')),
                PRIMARY KEY (bot_message_id, chat_id)
            );
            CREATE TABLE IF NOT EXISTS anonymous_links (
                id INTEGER PRIMARY KEY AUTOINCREMENT, owner_id INTEGER, link_code TEXT UNIQUE,
                is_active INTEGER DEFAULT 1, created_at TEXT DEFAULT (datetime('now')),
                last_used TEXT, message_count INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS force_channels (
                id INTEGER PRIMARY KEY AUTOINCREMENT, channel_id TEXT, channel_username TEXT,
                channel_title TEXT, button_title TEXT, added_at TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS bot_settings (key TEXT PRIMARY KEY, value TEXT);
            CREATE TABLE IF NOT EXISTS custom_buttons (
                id INTEGER PRIMARY KEY AUTOINCREMENT, panel_type TEXT, button_text TEXT,
                button_action TEXT, button_data TEXT, row_number INTEGER DEFAULT 0, position INTEGER DEFAULT 0
            );
            CREATE TABLE IF NOT EXISTS button_configs (
                id INTEGER PRIMARY KEY AUTOINCREMENT, panel_type TEXT, button_key TEXT,
                button_text TEXT, callback_data TEXT, row_number INTEGER DEFAULT 0,
                position INTEGER DEFAULT 0, is_visible INTEGER DEFAULT 1,
                UNIQUE(panel_type, button_key)
            );
            CREATE TABLE IF NOT EXISTS anon_messages (
                id INTEGER PRIMARY KEY AUTOINCREMENT, sender_id INTEGER, link_owner_id INTEGER,
                content_type TEXT, message_text TEXT, file_id TEXT, caption TEXT,
                timestamp TEXT DEFAULT (datetime('now'))
            );
            CREATE TABLE IF NOT EXISTS anon_blocks (
                id INTEGER PRIMARY KEY AUTOINCREMENT, link_owner_id INTEGER,
                blocked_user_id INTEGER, blocked_at TEXT DEFAULT (datetime('now')),
                UNIQUE(link_owner_id, blocked_user_id)
            );
        """)
        for k, v in DEFAULTS.items():
            await db.execute("INSERT OR IGNORE INTO bot_settings (key, value) VALUES (?, ?)", (k, v))
        for aid in MAIN_ADMINS:
            await db.execute("INSERT OR IGNORE INTO admins (user_id, added_by) VALUES (?, 0)", (aid,))
        for b in DEFAULT_USER_BUTTONS:
            await db.execute("INSERT OR IGNORE INTO button_configs (panel_type, button_key, button_text, callback_data, row_number, position) VALUES ('user', ?, ?, ?, ?, ?)", b)
        for b in DEFAULT_ADMIN_BUTTONS:
            await db.execute("INSERT OR IGNORE INTO button_configs (panel_type, button_key, button_text, callback_data, row_number, position) VALUES ('admin', ?, ?, ?, ?, ?)", b)
        await db.commit()
    finally:
        await db.close()


async def get_setting(key):
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT value FROM bot_settings WHERE key=?", (key,))
        return rows[0][0] if rows else DEFAULTS.get(key, "")
    finally:
        await db.close()


async def set_setting(key, value):
    db = await get_db()
    try:
        await db.execute("INSERT OR REPLACE INTO bot_settings (key, value) VALUES (?, ?)", (key, value))
        await db.commit()
    finally:
        await db.close()


async def add_user(uid, username=None, first_name=None):
    db = await get_db()
    try:
        await db.execute("INSERT INTO users (user_id, username, first_name) VALUES (?, ?, ?) ON CONFLICT(user_id) DO UPDATE SET username=excluded.username, first_name=excluded.first_name, last_activity=datetime('now')", (uid, username, first_name))
        await db.commit()
    finally:
        await db.close()


async def get_user(uid):
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT * FROM users WHERE user_id=?", (uid,))
        return dict(rows[0]) if rows else None
    finally:
        await db.close()


async def is_banned(uid):
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT is_banned FROM users WHERE user_id=?", (uid,))
        return bool(rows[0][0]) if rows else False
    finally:
        await db.close()


async def ban_user(uid):
    db = await get_db()
    try:
        await db.execute("UPDATE users SET is_banned=1 WHERE user_id=?", (uid,))
        await db.commit()
    finally:
        await db.close()


async def unban_user(uid):
    db = await get_db()
    try:
        await db.execute("UPDATE users SET is_banned=0 WHERE user_id=?", (uid,))
        await db.commit()
    finally:
        await db.close()


async def increment_messages(uid):
    db = await get_db()
    try:
        await db.execute("UPDATE users SET total_messages=total_messages+1, last_activity=datetime('now') WHERE user_id=?", (uid,))
        await db.commit()
    finally:
        await db.close()


async def get_all_user_ids():
    db = await get_db()
    try:
        return [r[0] for r in await db.execute_fetchall("SELECT user_id FROM users WHERE is_banned=0")]
    finally:
        await db.close()


async def get_user_count():
    db = await get_db()
    try:
        return (await db.execute_fetchall("SELECT COUNT(*) FROM users"))[0][0]
    finally:
        await db.close()


async def get_users_count_period(s, e):
    db = await get_db()
    try:
        return (await db.execute_fetchall("SELECT COUNT(*) FROM users WHERE join_date BETWEEN ? AND ?", (s, e)))[0][0]
    finally:
        await db.close()


async def get_top_users(limit=10):
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM users ORDER BY total_messages DESC LIMIT ?", (limit,))]
    finally:
        await db.close()


async def add_admin(uid, username=None, added_by=0):
    db = await get_db()
    try:
        await db.execute("INSERT OR REPLACE INTO admins (user_id, username, added_by) VALUES (?, ?, ?)", (uid, username, added_by))
        await db.commit()
    finally:
        await db.close()


async def remove_admin(uid):
    db = await get_db()
    try:
        await db.execute("DELETE FROM admins WHERE user_id=?", (uid,))
        await db.commit()
    finally:
        await db.close()


async def is_admin(uid):
    db = await get_db()
    try:
        return len(await db.execute_fetchall("SELECT 1 FROM admins WHERE user_id=?", (uid,))) > 0
    finally:
        await db.close()


async def get_all_admins():
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM admins ORDER BY added_at DESC")]
    finally:
        await db.close()


async def update_admin_activity(uid):
    db = await get_db()
    try:
        await db.execute("UPDATE admins SET last_activity=datetime('now') WHERE user_id=?", (uid,))
        await db.commit()
    finally:
        await db.close()


async def get_admin_ids():
    db = await get_db()
    try:
        return [r[0] for r in await db.execute_fetchall("SELECT user_id FROM admins")]
    finally:
        await db.close()


async def save_message(frm, tgt, ct, fid=None, txt=None, cap=None, is_adm=0, is_anon=0):
    db = await get_db()
    try:
        await db.execute("INSERT INTO messages (from_user_id, target_user_id, content_type, file_id, text, caption, is_from_admin, is_anonymous) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", (frm, tgt, ct, fid, txt, cap, is_adm, is_anon))
        await db.commit()
    finally:
        await db.close()


async def save_mapping(bmid, cid, tgt, orig, is_anon=0, link_own=0):
    db = await get_db()
    try:
        await db.execute("INSERT OR REPLACE INTO message_mapping (bot_message_id, chat_id, target_user_id, original_user_id, is_anonymous, link_owner_id) VALUES (?, ?, ?, ?, ?, ?)", (bmid, cid, tgt, orig, is_anon, link_own))
        await db.commit()
    finally:
        await db.close()


async def get_mapping(bmid, cid):
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT * FROM message_mapping WHERE bot_message_id=? AND chat_id=?", (bmid, cid))
        return dict(rows[0]) if rows else None
    finally:
        await db.close()


async def get_message_count():
    db = await get_db()
    try:
        return (await db.execute_fetchall("SELECT COUNT(*) FROM messages"))[0][0]
    finally:
        await db.close()


async def get_messages_count_period(s, e):
    db = await get_db()
    try:
        return (await db.execute_fetchall("SELECT COUNT(*) FROM messages WHERE timestamp BETWEEN ? AND ?", (s, e)))[0][0]
    finally:
        await db.close()


async def create_anon_link(oid, code):
    db = await get_db()
    try:
        await db.execute("INSERT INTO anonymous_links (owner_id, link_code) VALUES (?, ?)", (oid, code))
        await db.commit()
    finally:
        await db.close()


async def get_anon_link_by_code(code):
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT * FROM anonymous_links WHERE link_code=?", (code,))
        return dict(rows[0]) if rows else None
    finally:
        await db.close()


async def get_user_anon_links(oid):
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM anonymous_links WHERE owner_id=? ORDER BY created_at DESC", (oid,))]
    finally:
        await db.close()


async def get_all_anon_links():
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM anonymous_links ORDER BY created_at DESC")]
    finally:
        await db.close()


async def update_anon_link_usage(code):
    db = await get_db()
    try:
        await db.execute("UPDATE anonymous_links SET last_used=datetime('now'), message_count=message_count+1 WHERE link_code=?", (code,))
        await db.commit()
    finally:
        await db.close()


async def toggle_anon_link(code):
    db = await get_db()
    try:
        await db.execute("UPDATE anonymous_links SET is_active = 1 - is_active WHERE link_code=?", (code,))
        await db.commit()
    finally:
        await db.close()


async def delete_anon_link(code):
    db = await get_db()
    try:
        await db.execute("DELETE FROM anonymous_links WHERE link_code=?", (code,))
        await db.commit()
    finally:
        await db.close()


async def add_force_channel(cid, un, title, btn):
    db = await get_db()
    try:
        await db.execute("INSERT INTO force_channels (channel_id, channel_username, channel_title, button_title) VALUES (?, ?, ?, ?)", (cid, un, title, btn))
        await db.commit()
    finally:
        await db.close()


async def remove_force_channel(cid):
    db = await get_db()
    try:
        await db.execute("DELETE FROM force_channels WHERE channel_id=?", (cid,))
        await db.commit()
    finally:
        await db.close()


async def get_force_channels():
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM force_channels")]
    finally:
        await db.close()


async def add_custom_button(pt, bt, ba, bd="", rn=0, pos=0):
    db = await get_db()
    try:
        await db.execute("INSERT INTO custom_buttons (panel_type, button_text, button_action, button_data, row_number, position) VALUES (?, ?, ?, ?, ?, ?)", (pt, bt, ba, bd, rn, pos))
        await db.commit()
    finally:
        await db.close()


async def get_custom_buttons(pt):
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM custom_buttons WHERE panel_type=? ORDER BY row_number, position", (pt,))]
    finally:
        await db.close()


async def remove_custom_button(bid):
    db = await get_db()
    try:
        await db.execute("DELETE FROM custom_buttons WHERE id=?", (bid,))
        await db.commit()
    finally:
        await db.close()


async def get_button_configs(pt):
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM button_configs WHERE panel_type=? ORDER BY row_number, position", (pt,))]
    finally:
        await db.close()


async def get_button_config_by_key(key):
    db = await get_db()
    try:
        rows = await db.execute_fetchall("SELECT * FROM button_configs WHERE button_key=?", (key,))
        return dict(rows[0]) if rows else None
    finally:
        await db.close()


async def update_button_config(key, rn, pos, vis=None):
    db = await get_db()
    try:
        if vis is not None:
            await db.execute("UPDATE button_configs SET row_number=?, position=?, is_visible=? WHERE button_key=?", (rn, pos, vis, key))
        else:
            await db.execute("UPDATE button_configs SET row_number=?, position=? WHERE button_key=?", (rn, pos, key))
        await db.commit()
    finally:
        await db.close()


async def toggle_button_visibility(key):
    db = await get_db()
    try:
        await db.execute("UPDATE button_configs SET is_visible = 1 - is_visible WHERE button_key=?", (key,))
        await db.commit()
    finally:
        await db.close()


async def reset_button_configs(pt):
    db = await get_db()
    try:
        await db.execute("DELETE FROM button_configs WHERE panel_type=?", (pt,))
        await db.execute("DELETE FROM custom_buttons WHERE panel_type=?", (pt,))
        defaults = DEFAULT_USER_BUTTONS if pt == "user" else DEFAULT_ADMIN_BUTTONS
        for b in defaults:
            await db.execute("INSERT INTO button_configs (panel_type, button_key, button_text, callback_data, row_number, position) VALUES (?, ?, ?, ?, ?, ?)", (pt, *b))
        await db.commit()
    finally:
        await db.close()


async def get_all_panel_buttons(pt):
    configs = await get_button_configs(pt)
    customs = await get_custom_buttons(pt)
    result = []
    for c in configs:
        result.append({"source": "builtin", "key": c["button_key"], "text": c["button_text"], "callback": c["callback_data"], "row": c["row_number"], "pos": c["position"], "visible": c["is_visible"]})
    for c in customs:
        result.append({"source": "custom", "key": f"custom_{c['id']}", "text": c["button_text"], "callback": f"custom_{pt}_{c['id']}", "row": c["row_number"], "pos": c["position"], "visible": 1})
    result.sort(key=lambda x: (x["row"], x["pos"]))
    return result


async def save_anon_message(sid, lid, ct, mt="", fid="", cap=""):
    db = await get_db()
    try:
        await db.execute("INSERT INTO anon_messages (sender_id, link_owner_id, content_type, message_text, file_id, caption) VALUES (?, ?, ?, ?, ?, ?)", (sid, lid, ct, mt, fid, cap))
        await db.commit()
    finally:
        await db.close()


async def get_recent_anon_messages(lid, limit=20):
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM anon_messages WHERE link_owner_id=? ORDER BY timestamp DESC LIMIT ?", (lid, limit))]
    finally:
        await db.close()


async def get_all_recent_anon_messages(limit=50):
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM anon_messages ORDER BY timestamp DESC LIMIT ?", (limit,))]
    finally:
        await db.close()


async def get_anon_message_count():
    db = await get_db()
    try:
        return (await db.execute_fetchall("SELECT COUNT(*) FROM anon_messages"))[0][0]
    finally:
        await db.close()


async def get_anon_unique_senders():
    db = await get_db()
    try:
        return (await db.execute_fetchall("SELECT COUNT(DISTINCT sender_id) FROM anon_messages"))[0][0]
    finally:
        await db.close()


async def block_anon_sender(oid, bid):
    db = await get_db()
    try:
        await db.execute("INSERT OR IGNORE INTO anon_blocks (link_owner_id, blocked_user_id) VALUES (?, ?)", (oid, bid))
        await db.commit()
    finally:
        await db.close()


async def unblock_anon_sender(oid, bid):
    db = await get_db()
    try:
        await db.execute("DELETE FROM anon_blocks WHERE link_owner_id=? AND blocked_user_id=?", (oid, bid))
        await db.commit()
    finally:
        await db.close()


async def is_anon_blocked(oid, sid):
    db = await get_db()
    try:
        return len(await db.execute_fetchall("SELECT 1 FROM anon_blocks WHERE link_owner_id=? AND blocked_user_id=?", (oid, sid))) > 0
    finally:
        await db.close()


async def get_anon_blocks(oid):
    db = await get_db()
    try:
        return [dict(r) for r in await db.execute_fetchall("SELECT * FROM anon_blocks WHERE link_owner_id=?", (oid,))]
    finally:
        await db.close()


async def export_backup():
    db = await get_db()
    try:
        backup = {}
        for t in ["users", "admins", "messages", "message_mapping", "anonymous_links", "force_channels", "bot_settings", "custom_buttons", "button_configs", "anon_messages", "anon_blocks"]:
            backup[t] = [dict(r) for r in await db.execute_fetchall(f"SELECT * FROM {t}")]
        backup["_exported_at"] = datetime.datetime.utcnow().isoformat()
        return backup
    finally:
        await db.close()


async def import_backup(data):
    db = await get_db()
    try:
        for t in ["anon_blocks", "anon_messages", "button_configs", "custom_buttons", "force_channels", "bot_settings", "message_mapping", "messages", "anonymous_links", "admins", "users"]:
            if t not in data:
                continue
            await db.execute(f"DELETE FROM {t}")
            rows = data[t]
            if not rows:
                continue
            cols = list(rows[0].keys())
            ph = ", ".join(["?"] * len(cols))
            cn = ", ".join(cols)
            for row in rows:
                await db.execute(f"INSERT INTO {t} ({cn}) VALUES ({ph})", [row.get(c) for c in cols])
        await db.commit()
    finally:
        await db.close()
