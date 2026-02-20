import telebot
from telebot import types
from telebot.types import ReactionTypeEmoji

from app import app, db
from models import User   # اگر یوزر داخل models.py هست

import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv("TOKEN")
WEBAPP_URL = "https://ranjbarcoin.ir"   # لینک وب اپ

bot = telebot.TeleBot(TOKEN)

REFERRAL_REWARD = 1000

def set_menu_button():
    menu_btn = types.MenuButtonWebApp(
        type="web_app",   # ← این خط مهمه
        text="Play",
        web_app=types.WebAppInfo(WEBAPP_URL)
    )

    bot.set_chat_menu_button(menu_button=menu_btn)
    
# -------------------------------
# گرفتن یا ساخت یوزر + آپدیت پروفایل
# -------------------------------
def get_or_create_user(tg_user):
    user = User.query.filter_by(telegram_id=str(tg_user.id)).first()
    is_new = False

    if not user:
        is_new = True
        user = User(
            telegram_id=str(tg_user.id),
            username=tg_user.username,
            first_name=tg_user.first_name,
            last_name=tg_user.last_name,
        )
        db.session.add(user)
    else:
        user.username = tg_user.username
        user.first_name = tg_user.first_name
        user.last_name = tg_user.last_name
        
    db.session.commit()
    return user, is_new



# -------------------------------
# /////////////start/////////////
# -------------------------------
@bot.message_handler(commands=["start"])
def start(message):
    
    with app.app_context():
        
        user, is_new = get_or_create_user(message.from_user)
        set_menu_button()
    
        args = message.text.split()
        referral_code = None
    
        if len(args) > 1:
            referral_code = args[1]
            
        
        markup = types.InlineKeyboardMarkup()
        markup.add(
            types.InlineKeyboardButton(
                text="🚀 Open App",
                web_app=types.WebAppInfo(WEBAPP_URL)
            )
        )
    
        if is_new:
            text = (
                "Welcome to <b>Ranjbar Coin</b> 🪙\n\n"
                "Start mining and upgrade your power.\n"
                "You can check your status anytime using /me\n"
                "If you find any bugs, please contact @mirbehresi1"
            )
        else:
            text = (
                "Welcome back 🪙\n\n"
                "Continue mining and climb the leaderboard!\n"
                "Use /me to check your current stats."
                "If you find any bugs, please contact @mirbehresi1"
            )
            
        # Referral Logic
        if is_new and referral_code and not user.referrer_id:
            with app.app_context():
                referrer = User.query.filter_by(
                    telegram_id=str(referral_code)
                ).first()
    
                if referrer and referrer.telegram_id != str(user.telegram_id):
    
                    user.referrer_id = referrer.id
    
                    # 🎁 Reward
                    referrer.balance += REFERRAL_REWARD
                    referrer.total_earned += REFERRAL_REWARD
                    referrer.referrals_count += 1
    
                    db.session.commit()
    
                    bot.send_message(
                        referrer.telegram_id,
                        f"🎉 You earned {REFERRAL_REWARD} RBC for inviting a new player!"
                    )
        
        bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="HTML")
        bot.set_message_reaction(message.chat.id, message.id, [ReactionTypeEmoji('🤝')], is_big=False)



# -------------------------------
# ///////////get status////////
# -------------------------------
@bot.message_handler(commands=["me"])
def me(message):
    with app.app_context():
        user = User.query.filter_by(
            telegram_id=str(message.from_user.id)
        ).first()
        Referrals: {user.referrals_count}
        if not user:
            bot.reply_to(message, "User not found. please /start the bot. ")
            return

        text = f"""
                Username: @{user.username}
                First name: {user.first_name}
                Last name: {user.last_name}
                Balance: {user.balance} 🪙
                Energy: {user.energy}/{user.max_energy} ⚡
                Referrals: {user.referrals_count} 👥
                """
        bot.set_message_reaction(message.chat.id, message.id, [ReactionTypeEmoji('👍')], is_big=False)
        bot.reply_to(message, text)
        


# -------------------------------
#//////////running///////////////
# -------------------------------
if __name__ == "__main__":
    print("Bot is running...")
    bot.infinity_polling(skip_pending=True)
