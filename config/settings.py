import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Bot configuration
    BOT_TOKEN = os.getenv("TOKEN")
    
    # Group verification
    TELEGRAM_GROUP = "https://t.me/+2_-i4vuiQZc0OTRk"
    # https://t.me/borelpronscoupon
    GROUP_USERNAME = "borelpronscoupon"
    GROUP_ID = -1002865381319
    
    # Promo codes
    PROMO_CODE = "ARIS60"
    
    # Linkss
    LINKS = {
        '1xbet': 'https://urls.fr/j0C9yU',
        'betwinne': 'https://bwredir.com/2qUY?p=%2Fregistration%2F',
        'melbet': 'https://refpakrtsb.top/L?tag=d_4475033m_45415c_&site=4475033&ad=45415',
        'winwin': 'https://refpa443273.top/L?tag=d_4440428m_64485c_&site=4440428&ad=64485'
    }
    # Database
    DATABASE_PATH = "data/users.json"
    ADMIN_ID = "7290873070" 
    
    # Cooldowns (in seconds)
    PREDICTION_COOLDOWN = 40
    GAME_COOLDOWN = 30
    
    # Referral system
    REFERRAL_BONUS = 1000
    MIN_REFERRALS_FOR_BONUS = 5