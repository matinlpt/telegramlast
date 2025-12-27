import telebot
from telebot import types
from datetime import datetime
import pytz
import jdatetime
import threading
import time
import random
import string
import os

# ─── تنظیمات ───
BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(BOT_TOKEN)
CHANNEL_USERNAME = "@music176176"
ADMIN_ID = 7261582672

# ─── ذخیره مکالمات و نام‌های مستعار ───
conversations = {}
aliases = {}

def generate_alias():
    letters = string.ascii_uppercase
    numbers = ''.join(random.choices(letters, k=2)) + str(random.randint(10, 99))
    return f"کاربر #{numbers}"

# ─── تابع زمان و تاریخ ───
def get_dates():
    tehran_tz = pytz.timezone('Asia/Tehran')
    now = datetime.now(tehran_tz)
    j_now = jdatetime.datetime.fromgregorian(datetime=now)
    miladi_date = now.strftime("%Y/%m/%d")
    shamsi_date = j_now.strftime("%Y/%m/%d")
    days_left = (datetime(2026, 3, 20, tzinfo=tehran_tz) - now).days
    return now, shamsi_date, miladi_date, days_left

# ─── منوی اصلی (موزیک ردیف کامل + 2x2 زیرش) ───
def main_menu():
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    btn_music = types.KeyboardButton("🎵 ارسال موزیک")
    btn_today = types.KeyboardButton("📅 وضعیت امروز")
    btn_chat = types.KeyboardButton("🕶 چت ناشناس")
    btn_about = types.KeyboardButton("ℹ️ درباره بات")
    btn_end = types.KeyboardButton("❌ پایان چت ناشناس")
    markup.row(btn_music) # یک ردیف کامل بالا
    markup.row(btn_today, btn_chat) # ردیف دوم (دو در دو)
    markup.row(btn_about, btn_end) # ردیف سوم (دو در دو)
    return markup

# ─── start ───
@bot.message_handler(commands=['start'])
def start_message(message):
    bot.reply_to(
        message,
        "🎧 به ربات چنل Cocane خوش اومدی!\n"
        "از منوی پایین یکیو انتخاب کن 👇",
        reply_markup=main_menu()
    )

# ─── ارسال موزیک ───
@bot.message_handler(func=lambda m: m.text == "🎵 ارسال موزیک")
def request_music(message):
    # کاربر می‌تونه یه بار موزیک بفرسته؛ برای سادگی این نسخه فقط راهنمایی میده
    bot.reply_to(message, "یه موزیک بفرست 🎶 (فقط یکی)\nاگه دوباره خواستی بفرستی، دوباره دکمه 🎵 رو بزن 🔁")

@bot.message_handler(content_types=['audio', 'voice', 'document'])
def handle_audio(message):
    chat_id = message.chat.id
    # فوروارد به ادمین و ریپلای تشکر
    try:
        bot.forward_message(ADMIN_ID, chat_id, message.message_id)
    except Exception:
        # اگه forward نشد سعی می‌کنیم به صورت پیام ارسال کنیم
        try:
            bot.send_message(ADMIN_ID, f"یک آهنگ از کاربر {aliases.get(chat_id, 'ناشناس')} (chat_id: {chat_id})")
            bot.forward_message(ADMIN_ID, chat_id, message.message_id)
        except Exception as e:
            print("Error forwarding music:", e)
    bot.reply_to(message, "مرسی از موزیکت 🎧\nاگه خواستی باز بفرستی، دوباره روی 🎵 بزن.")

# ─── وضعیت امروز ───
@bot.message_handler(func=lambda m: m.text == "📅 وضعیت امروز")
def today_status(message):
    now, shamsi, miladi, left = get_dates()
    bot.reply_to(
        message,
        f"🕓 {now.strftime('%H:%M')}\n"
        f"📅 تاریخ شمسی: {shamsi}\n"
        f"🌍 تاریخ میلادی: {miladi}\n"
        f"📆 روزهای باقی‌مانده تا عید: {left} روز"
    )

# ─── چت ناشناس ───
@bot.message_handler(func=lambda m: m.text == "🕶 چت ناشناس")
def hidden_chat(message):
    chat_id = message.chat.id
    if chat_id == ADMIN_ID:
        bot.send_message(chat_id, "مدیر نمی‌تونه با خودش چت ناشناس شروع کنه 😅")
        return

    alias = generate_alias()
    aliases[chat_id] = alias
    # نگاشت دوطرفه: کاربر -> ادمین و ادمین -> کاربر
    conversations[chat_id] = ADMIN_ID
    conversations[ADMIN_ID] = chat_id

    bot.send_message(chat_id, "📩 چت ناشناس با مدیر شروع شد! هرچی بنویسی میره براش 💬")
    bot.send_message(ADMIN_ID, f"🔔 یه مکالمه جدید شروع شد با {alias} 🕊️")

# ─── پایان چت ───
@bot.message_handler(func=lambda m: m.text == "❌ پایان چت ناشناس")
def end_chat(message):
    chat_id = message.chat.id
    if chat_id in conversations:
        other = conversations.pop(chat_id)
        # حذف نگاشت معکوس اگر وجود داشته باشه
        if other in conversations:
            conversations.pop(other)
        alias = aliases.get(chat_id, "کاربر ناشناس")
        bot.send_message(chat_id, "🚫 چت ناشناس تموم شد. برای شروع دوباره روی 🕶 چت ناشناس بزن.")
        if chat_id != ADMIN_ID:
            bot.send_message(ADMIN_ID, f"📴 چت با {alias} بسته شد.")
        aliases.pop(chat_id, None)
    else:
        bot.send_message(chat_id, "هیچ چت فعالی نداری 😅")

# ─── درباره بات ───
@bot.message_handler(func=lambda m: m.text == "ℹ️ درباره بات")
def about_bot(message):
    bot.reply_to(
        message,
        "🎧 این ربات برای اشتراک موزیک و ارتباط مستقیم ساخته شده.\n"
        "⭐ طراحی و برنامه‌نویسی توسط متین امانی ⭐\n"
        "📍 چنل: t.me/music176176"
    )

# ─── هندل پیام‌ها ───
@bot.message_handler(func=lambda m: True)
def handle_messages(message):
    chat_id = message.chat.id

    # اگر پیام از کاربر عادی اومد
    if chat_id != ADMIN_ID:
        # اگر کاربر در یک گفتگو ناشناس باشه
        if chat_id in conversations:
            alias = aliases.get(chat_id, "کاربر ناشناس")
            # ارسال پیام به ادمین و بروزرسانی نگاشت ادمین -> این کاربر
            try:
                bot.send_message(ADMIN_ID, f"💭 از {alias}:\n{message.text}")
                # مهم: حتماً ادمین را به آخرین کاربر فعال وصل می‌کنیم
                conversations[ADMIN_ID] = chat_id
            except Exception as e:
                bot.reply_to(message, f"❌ خطا در ارسال: {e}")
        else:
            bot.send_message(chat_id, "برای چت ناشناس روی 🕶 چت ناشناس بزن 💌")

    # اگر پیام از ادمین اومد
    else:
        # اگر ادمین به یک کاربر وصل هست
        if ADMIN_ID in conversations:
            target_id = conversations.get(ADMIN_ID)
            if target_id:
                try:
                    bot.send_message(target_id, f"📨 مدیر:\n{message.text}")
                except Exception as e:
                    bot.send_message(ADMIN_ID, f"❌ خطا در ارسال به کاربر: {e}")
            else:
                bot.send_message(ADMIN_ID, "❗️الان با هیچ کاربری در چت ناشناس نیستی.")
        else:
            bot.send_message(ADMIN_ID, "❗️الان با هیچ کاربری در چت ناشناس نیستی.")

# ─── پیام‌های خودکار (تصاویر صبح/شب) ───
def daily_messages():
    last_night_message = None
    while True:
        now, shamsi, miladi, left = get_dates()
        hour = now.hour

        # صبح بخیر
        if hour == 10 and now.minute == 0:
            if last_night_message:
                try:
                    bot.delete_message(CHANNEL_USERNAME, last_night_message)
                except:
                    pass
            bot.send_photo(
                CHANNEL_USERNAME,
                photo="https://i.imgur.com/BRF7eQF.jpeg",
                caption=(
                    f"☀️ صبح بخیر دوستان 🎧\n"
                    f"📅 {shamsi} | {miladi}\n"
                    "یه روز تازه، یه حس تازه 🎶"
                )
            )

        # شب بخیر
        elif hour == 22 and now.minute == 0:
            sent = bot.send_photo(
                CHANNEL_USERNAME,
                photo="https://i.imgur.com/lo2CJAl.jpeg",
                caption=(
                    "🌙 شب بخیر رفیقا 💫\n"
                    "وقتشه آهنگارو پلی کنی و ریلکس کنی 🎧"
                )
            )
            last_night_message = sent.message_id

        time.sleep(60)

# ─── اجرای ربات ───
threading.Thread(target=daily_messages, daemon=True).start()
print("بات فعال شد ✅")
bot.infinity_polling()

