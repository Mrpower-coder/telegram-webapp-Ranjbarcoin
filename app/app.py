from flask import Flask, jsonify, render_template, request
from config import Config
from database import db
from models import User
from datetime import datetime

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

UPGRADES = {
    "power": {
        "base_price": 250,
        "max_level": 20
    },
    "energy": {
        "base_price": 300,
        "max_level": 15
    },
    "regen": {
        "base_price": 500,
        "max_level": 10
    }
}


LEVELS = [
    (0, "🧸 پیش‌دبستانی"),
    (2000, "🎒 دبستانی"),
    (8000, "📘 راهنمایی"),
    (20000, "📗 دبیرستانی"),
    (50000, "📙 کارشناسی"),
    (100000, "🎓 کارشناسی ارشد"),
    (150000, "👨‍🏫 دکتری"),
    (200000, "👑 پروفسور"),
]


with app.app_context():
    db.create_all()

def get_level_data(total_earned):
    current = LEVELS[0]
    next_level = None

    for i in range(len(LEVELS)):
        if total_earned >= LEVELS[i][0]:
            current = LEVELS[i]
            if i + 1 < len(LEVELS):
                next_level = LEVELS[i + 1]
        else:
            break

    if next_level:
        progress = total_earned - current[0]
        needed = next_level[0] - current[0]
        percent = int((progress / needed) * 100)
        remaining = next_level[0] - total_earned
    else:
        percent = 100
        remaining = 0

    return {
        "title": current[1],
        "percent": percent,
        "remaining": remaining
    }


def get_or_create_user(telegram_user):
    """Retrieve existing user or create a new one based on telegram_user"""
    user = User.query.filter_by(telegram_id=str(telegram_user.id)).first()
    if not user:
        user = User(
            telegram_id=str(telegram_user.id),
            username=telegram_user.username,
            first_name=telegram_user.first_name,
            last_name=telegram_user.last_name
        )
        db.session.add(user)
        db.session.commit()
    else:
        updated = False
        if user.username != telegram_user.username:
            user.username = telegram_user.username
            updated = True
        if user.first_name != telegram_user.first_name:
            user.first_name = telegram_user.first_name
            updated = True
        if user.last_name != telegram_user.last_name:
            user.last_name = telegram_user.last_name
            updated = True
        if updated:
            db.session.commit()
    return user


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/state", methods=["POST"])
def state():
    data = request.get_json()
    telegram_id = data.get("user_id")
    if not telegram_id:
        return jsonify({"error": "No user_id provided"}), 400

    user = User.query.filter_by(telegram_id=str(telegram_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.regenerate_energy()
    db.session.commit()
    
    level_data = get_level_data(user.total_earned)
    
    return jsonify(
        balance=user.balance,
        energy=user.energy,
        max_energy=user.energy_cap(),
        power_level=user.power_level,
        energy_level=user.energy_level,
        regen_level=user.regen_level,
        level=level_data["title"],
        level_percent=level_data["percent"],
        level_remaining=level_data["remaining"],
        )



@app.route("/mine", methods=["POST"])
def mine():
    data = request.get_json()
    telegram_id = data.get("user_id")
    if not telegram_id:
        return jsonify({"error": "No user_id provided"}), 400

    user = User.query.filter_by(telegram_id=str(telegram_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    user.regenerate_energy()
    if user.energy <= 0:
        return jsonify({"error": "No energy"}), 400

    power = user.mine_power()   # ← محاسبه مقدار ماین
    user.energy -= 1
    user.balance += power
    user.total_earned += power

    db.session.commit()
    
    level_data = get_level_data(user.total_earned)

    return jsonify(
        balance=user.balance,
        energy=user.energy,
        max_energy=user.max_energy,
        mine_power=power,
        level=level_data["title"],
        level_percent=level_data["percent"],
        level_remaining=level_data["remaining"],
    )




@app.route("/leaderboard")
def leaderboard():
    top_users = User.query.order_by(User.balance.desc()).limit(3).all()
    return render_template("leaderboard.html", users=top_users)
    

@app.route("/upgrades/state", methods=["GET"])
def upgrades_state():
    telegram_id = request.args.get("user_id")  # ← تغییر این خط

    if not telegram_id:
        return jsonify({"error": "No user_id provided"}), 400

    user = User.query.filter_by(telegram_id=str(telegram_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "power": {
            "level": user.power_level,
            "price": upgrade_price(
                UPGRADES["power"]["base_price"],
                user.power_level + 1
            )
        },
        "energy": {
            "level": user.energy_level,
            "price": upgrade_price(
                UPGRADES["energy"]["base_price"],
                user.energy_level + 1
            )
        },
        "regen": {
            "level": user.regen_level,
            "price": upgrade_price(
                UPGRADES["regen"]["base_price"],
                user.regen_level + 1
            )
        }
    })


@app.route("/upgrade", methods=["POST"])
def upgrade():
    data = request.get_json()
    telegram_id = data.get("user_id")
    upgrade_type = data.get("type")  # power | energy | regen

    if upgrade_type not in UPGRADES:
        return jsonify({"error": "Invalid upgrade type"}), 400

    user = User.query.filter_by(telegram_id=str(telegram_id)).first()
    if not user:
        return jsonify({"error": "User not found"}), 404

    config = UPGRADES[upgrade_type]

    # get current level
    level_attr = f"{upgrade_type}_level"
    current_level = getattr(user, level_attr)

    if current_level >= config["max_level"]:
        return jsonify({"error": "Max level reached"}), 400

    price = upgrade_price(config["base_price"], current_level + 1)

    if user.balance < price:
        return jsonify({"error": "Not enough balance"}), 400

    # apply upgrade
    user.balance -= price
    setattr(user, level_attr, current_level + 1)

    # اگر انرژی آپگرید شد، سقف رو هم اصلاح کن
    if upgrade_type == "energy":
        user.max_energy = user.energy_cap()
        user.energy = min(user.energy, user.max_energy)

    db.session.commit()

    return jsonify({
        "success": True,
        "type": upgrade_type,
        "new_level": current_level + 1,
        "balance": user.balance
    })


def upgrade_price(base_price: int, level: int) -> int:
    """
    Calculate upgrade price based on level
    price = base * (level ^ 2.7)
    """
    return int(base_price * (level ** 2.7))

@app.route("/upgrades")
def upgrades_page():
    """
    Serve the upgrades HTML page
    """
    return render_template("upgrade.html")

    
@app.route("/info")
def info():
    return render_template("info.html")


@app.route("/donate")
def donate():
    return render_template("donate.html")


if __name__ == "__main__":
    app.run()
