import io
import os
import string
import secrets
import datetime
import json
import psutil
from PIL import Image
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas as pdf_canvas
import qrcode


def get_server_status() -> dict:
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage("/")
    return {
        "cpu_percent": cpu_percent,
        "cpu_count": psutil.cpu_count(),
        "ram_total": round(memory.total / (1024 ** 3), 2),
        "ram_used": round(memory.used / (1024 ** 3), 2),
        "ram_free": round(memory.available / (1024 ** 3), 2),
        "ram_percent": memory.percent,
        "disk_total": round(disk.total / (1024 ** 3), 2),
        "disk_used": round(disk.used / (1024 ** 3), 2),
        "disk_free": round(disk.free / (1024 ** 3), 2),
        "disk_percent": disk.percent,
        "hostname": os.uname().nodename if hasattr(os, "uname") else "N/A",
    }


def format_server_status(status: dict) -> str:
    return (
        "🖥️ <b>وضعیت سرور</b>\n\n"
        f"🏷️ نام سرور: <code>{status['hostname']}</code>\n"
        f"⚙️ پردازنده: {status['cpu_count']} هسته — {status['cpu_percent']}٪ استفاده\n"
        f"💾 رم: {status['ram_used']}GB / {status['ram_total']}GB ({status['ram_percent']}٪)\n"
        f"📀 دیسک: {status['disk_used']}GB / {status['disk_total']}GB ({status['disk_percent']}٪)\n"
    )


def get_date_range(period: str):
    now = datetime.datetime.utcnow()
    if period == "daily":
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "weekly":
        start = (now - datetime.timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
    elif period == "monthly":
        start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    elif period == "yearly":
        start = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    else:
        start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    return start.isoformat(), now.isoformat()


async def image_to_pdf(image_bytes: bytes) -> bytes:
    image = Image.open(io.BytesIO(image_bytes))
    if image.mode in ("RGBA", "P"):
        image = image.convert("RGB")
    buf = io.BytesIO()
    image.save(buf, format="PDF", resolution=100.0)
    return buf.getvalue()


async def convert_image(image_bytes: bytes, from_fmt: str, to_fmt: str) -> bytes:
    image = Image.open(io.BytesIO(image_bytes))
    if to_fmt.lower() in ("jpg", "jpeg"):
        if image.mode in ("RGBA", "P"):
            image = image.convert("RGB")
    buf = io.BytesIO()
    fmt = "JPEG" if to_fmt.lower() in ("jpg", "jpeg") else to_fmt.upper()
    image.save(buf, format=fmt)
    return buf.getvalue()


async def generate_qr(text: str) -> tuple:
    qr = qrcode.QRCode(version=1, box_size=10, border=4)
    qr.add_data(text)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue(), text


def generate_password(length: int = 16, level: str = "hard") -> str:
    levels = {
        "easy": string.ascii_lowercase,
        "medium": string.ascii_letters,
        "hard": string.ascii_letters + string.digits,
        "strong": string.ascii_letters + string.digits + "!@#$%^&*()-_=+[]{}|;:,.<>?",
    }
    charset = levels.get(level, levels["hard"])
    return "".join(secrets.choice(charset) for _ in range(length))


def format_user_info(user: dict) -> str:
    name = user.get("first_name", "ناشناس")
    uid = user.get("user_id", "?")
    uname = f"@{user['username']}" if user.get("username") else "ندارد"
    msgs = user.get("total_messages", 0)
    return f"👤 {name} | ID: <code>{uid}</code> | {uname} | 📩 {msgs} پیام"
