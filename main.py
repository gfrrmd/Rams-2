import os
import re
import io
import asyncio
from datetime import datetime, timedelta

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    filters, ContextTypes, ConversationHandler
)
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import SessionPasswordNeededError, PhoneCodeInvalidError, PhoneCodeExpiredError
from telethon.tl.types import (
    MessageMediaPhoto, MessageMediaDocument,
    DocumentAttributeVideo, DocumentAttributeFilename,
    InputPeerChannel
)

from database import (
    init_db, upsert_user,
    save_user_session, get_user_session, delete_user_session,
    is_subscribed, get_subscription_info, activate_subscription, revoke_subscription,
    get_user_by_username, get_auto_dl_view_once, set_auto_dl_view_once
)

# ENV VARS
BOT_TOKEN   = os.environ["BOT_TOKEN"]
ADMIN_ID    = int(os.environ["ADMIN_ID"])

DEVICE_MODEL     = "iPhone 17 Pro Max"
SYSTEM_VERSION   = "iOS 26.4"
APP_VERSION      = "11.4.1"
LANG_CODE        = "id"
SYSTEM_LANG_CODE = "id-ID"

API_ID_STEP, API_HASH_STEP, PHONE_STEP, CODE_STEP, PASSWORD_STEP = range(5)

waiting_restore = set()
waiting_gift    = set()
waiting_revoke  = set()

temp_store     = {}
active_clients = {}

# DEDUP & LOCK
dl_locks: dict[int, asyncio.Lock] = {}
dl_seen:  dict[int, set]          = {}


TG_LINK_RE = re.compile(
    r"(?:https?://)?t\.me/"
    r"(?:c/(?P<channel_id>\d+)/(?P<msg_id2>\d+)|"
    r"(?P<username>[a-zA-Z0-9_]+)/(?P<msg_id>\d+))"
)


# ── HELPERS ───────────────────────────────────────────────────────
def build_client(api_id, api_hash, session_string=""):
    return TelegramClient(
        StringSession(session_string), api_id, api_hash,
        device_model=DEVICE_MODEL, system_version=SYSTEM_VERSION,
        app_version=APP_VERSION, lang_code=LANG_CODE,
        system_lang_code=SYSTEM_LANG_CODE
    )


def escape_md(text):
    if not text:
        return "Unknown"
    for ch in ["[", "]", "(", ")", "*", "_", "`"]:
        text = text.replace(ch, f"\\{ch}")
    return text


def is_no_forward(message):
    return bool(getattr(message, "noforwards", False))


def is_sticker_doc(doc):
    if doc is None:
        return False
    mime = getattr(doc, "mime_type", "") or ""
    has_stickerset = any(
        getattr(attr, "stickerset", None) is not None
        for attr in getattr(doc, "attributes", [])
    )
    return has_stickerset or "sticker" in mime


def get_video_attributes(doc):
    if doc is None:
        return None
    for attr in getattr(doc, "attributes", []):
        if isinstance(attr, DocumentAttributeVideo):
            return attr
    return None


def get_file_name(doc):
    if doc is None:
        return None
    for attr in getattr(doc, "attributes", []):
        if isinstance(attr, DocumentAttributeFilename):
            return attr.file_name
    return None


def _dl_dedup_check(user_id: int, event_id: int) -> bool:
    seen = dl_seen.setdefault(user_id, set())
    if event_id in seen:
        return True
    seen.add(event_id)
    if len(seen) > 50:
        to_remove = list(seen)[:25]
        for x in to_remove:
            seen.discard(x)
    return False


def _clear_user_state(uid: int):
    temp_store.pop(uid, None)
    waiting_restore.discard(uid)
    waiting_gift.discard(uid)
    waiting_revoke.discard(uid)


def _format_progress(current: int, total: int) -> str:
    if total <= 0:
        return "0.00%"
    return f"{(current / total) * 100:.2f}%"


async def download_bytes_with_progress(client, media, status_msg, start_text="⏳ Sedang mendownload media... 0.00%"):
    try:
        await status_msg.edit(start_text)
    except Exception:
        pass

    loop = asyncio.get_running_loop()
    state = {"last_ts": 0.0, "last_pct": -1.0}

    async def _progress(current, total):
        now = loop.time()
        pct = (current / total * 100) if total else 0.0
        if (now - state["last_ts"] < 0.8) and (pct - state["last_pct"] < 1.0):
            return
        state["last_ts"] = now
        state["last_pct"] = pct
        try:
            await status_msg.edit(f"⏳ Sedang mendownload media... {_format_progress(current, total)}")
        except Exception:
            pass

    return await client.download_media(media, bytes, progress_callback=_progress)


async def stop_client_for_user(user_id: int):
    """
    Disconnect dan hapus client Telethon untuk user tertentu.
    Dipanggil saat VIP direvoke atau expired.
    """
    client = active_clients.pop(user_id, None)
    if client:
        try:
            if client.is_connected():
                await client.disconnect()
            print(f"🔴 Client dihentikan untuk user {user_id} (VIP tidak aktif)")
        except Exception as e:
            print(f"⚠️ Gagal disconnect client user {user_id}: {e}")
    # Bersihkan dedup & lock
    dl_locks.pop(user_id, None)
    dl_seen.pop(user_id, None)


def main_keyboard(uid):
    rows = [
        [InlineKeyboardButton("⚙️ Setup Session", callback_data="menu_setup")],
        [
            InlineKeyboardButton("✨ Fitur VIP", callback_data="menu_fitur"),
            InlineKeyboardButton("💎 Beli VIP", callback_data="menu_beli"),
        ],
        [
            InlineKeyboardButton("⌛️ Status Langganan", callback_data="menu_subscription"),
            InlineKeyboardButton("📖 Cara Penggunaan", callback_data="menu_guide"),
        ]
    ]
    if uid == ADMIN_ID:
        rows.append([InlineKeyboardButton("👤 Menu Admin", callback_data="menu_admin")])
    return InlineKeyboardMarkup(rows)


def admin_keyboard():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("📦 Backup DB", callback_data="admin_backup"),
            InlineKeyboardButton("♻️ Restore DB", callback_data="admin_restore"),
        ],
        [
            InlineKeyboardButton("🎁 Gift VIP", callback_data="admin_gift"),
            InlineKeyboardButton("🚫 Revoke VIP", callback_data="admin_revoke"),
        ],
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_back")],
    ])




def fitur_vip_keyboard(uid):
    auto_on = get_auto_dl_view_once(uid)
    label = f"⏱️ Auto DL Timer/View-Once: {'ON ✅' if auto_on else 'OFF ❌'}"
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(label, callback_data="vip_toggle_auto_dl")],
        [InlineKeyboardButton("💎 Beli VIP", callback_data="menu_beli")],
        [InlineKeyboardButton("🔙 Kembali", callback_data="menu_back")],
    ])
FITUR_VIP_TEXT = (
    "✨ *Fitur VIP Rams Bot — Langsung Kamu Bisa Gunakan*\n\n"
    "Pakai bot ini, kamu bisa:\n\n"
    "📸 *Download Media Timer/View-Once (.dl)*\n"
    "Simpan foto atau video timer yang hanya bisa dilihat sekali langsung ke akun kamu. "
    "Reply media → ketik `.dl` → langsung tersimpan ke Saved Messages.\n\n"
    "📣 *Download Konten dari Channel/Grup Private (.copy)*\n"
    "Ambil foto, video, dokumen, atau teks dari channel/grup yang tidak bisa di-forward/simpan. "
    "Kirim `.copy <link>` → konten langsung dikirim ke kamu.\n\n"
    "✅ *Bypass Batas No-Forward*\n"
    "Akses media dari channel yang blokir fitur forward, tanpa perlu screenshot.\n\n"
    "✅ *Support Semua Format*\n"
    "Bisa untuk foto, video, GIF, audio, stiker, dan dokumen.\n\n"
    "━━━━━━━━━━━━━━━━━\n"
    "💡 *Cara Mulai:*\n"
    "1. Beli VIP lewat tombol di bawah\n"
    "2. Jalankan /setup untuk setup session\n"
    "3. Langsung pakai `.dl` atau `.copy` di chat manapun"
)

GUIDE_TEXT = (
    "📖 *Panduan Penggunaan Rams VIP Bot*\n\n"
    "━━━━━━━━━━━━━━━━━\n"
    "🔹 *Command .dl — Download Media*\n"
    "Digunakan untuk mendownload media view-once (sekali lihat) atau "
    "media dari chat restricted yang tidak bisa di-forward.\n\n"
    "*Cara pakai:*\n"
    "1. Buka chat yang ada media view-once atau restricted\n"
    "2. Reply (balas) pesan media tersebut\n"
    "3. Ketik `.dl` lalu kirim\n"
    "4. Media akan otomatis tersimpan di Saved Messages kamu\n\n"
    "⚠️ Pastikan kamu sudah reply ke pesan medianya, bukan ke pesan teks biasa.\n\n"
    "━━━━━━━━━━━━━━━━━\n"
    "🔹 *Command .copy — Copy dari Channel/Grup*\n"
    "Digunakan untuk menyalin konten (foto, video, dokumen, teks) dari "
    "channel atau grup yang tidak mengizinkan forward.\n\n"
    "*Cara pakai:*\n"
    "1. Buka pesan yang ingin di-copy di channel/grup\n"
    "2. Salin link pesan (klik kanan pesan lalu Copy Link)\n"
    "3. Ketik `.copy <link>` di chat mana saja\n"
    "4. Konten akan dikirim ke Saved Messages kamu\n\n"
    "*Format link yang didukung:*\n"
    "\u2022 Public: `.copy https://t.me/namaChannel/123`\n"
    "\u2022 Private: `.copy https://t.me/c/1234567890/123`\n\n"
    "⚠️ Untuk channel private, akun kamu harus sudah bergabung ke channel tersebut.\n\n"
    "━━━━━━━━━━━━━━━━━\n"
    "💡 *Tips:*\n"
    "\u2022 Semua hasil download dikirim ke Saved Messages akun Telegram kamu\n"
    "\u2022 Pastikan session sudah di-setup via /setup sebelum menggunakan fitur ini\n"
    "\u2022 Fitur ini hanya tersedia untuk pengguna VIP aktif"
)

