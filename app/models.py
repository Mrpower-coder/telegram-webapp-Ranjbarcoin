from database import db
from datetime import datetime


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    telegram_id = db.Column(db.String, unique=True)
    username = db.Column(db.String)
    first_name = db.Column(db.String)
    last_name = db.Column(db.String)
    
    # Referral system
    referrer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=True)
    referrals_count = db.Column(db.Integer, default=0)

    # اقتصاد
    balance = db.Column(db.Integer, default=0)

    # انرژی
    energy = db.Column(db.Integer, default=100)
    max_energy = db.Column(db.Integer, default=100)
    last_energy_time = db.Column(db.DateTime, default=datetime.utcnow)

    # 🔼 Upgrade levels
    power_level = db.Column(db.Integer, default=1)   # قدرت ماین
    energy_level = db.Column(db.Integer, default=1)  # سقف انرژی
    regen_level = db.Column(db.Integer, default=1)   # سرعت رجن انرژی
    
    total_earned = db.Column(db.Integer, default=0)
    # ------------------------
    # منطق انرژی
    # ------------------------
    def regenerate_energy(self):
        now = datetime.utcnow()
        diff = int((now - self.last_energy_time).total_seconds())

        # هر لول رجن → سریع‌تر
        regen_interval = max(1, 3 - (self.regen_level - 1))
        regen = diff // regen_interval

        if regen > 0:
            self.energy = min(self.energy_cap(), self.energy + regen)
            self.last_energy_time = now

    # ------------------------
    # مقادیر محاسباتی
    # ------------------------
    def mine_power(self):
        """
        مقدار سکه‌ای که هر بار ماین می‌گیرد
        """
        return 1 + (self.power_level - 1)

    def energy_cap(self):
        """
        سقف انرژی بر اساس لول
        """
        return 100 + (self.energy_level - 1) * 20
