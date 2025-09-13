from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts

class ReferralSystem:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.texts = load_texts()
        
    async def handle_referral(self, user_id, referrer_id):
        """Gérer un nouveau parrainage"""
        try:
            referrer_id = int(referrer_id)
            
            # Vérifier que l'utilisateur n'est pas déjà parrainé
            user_data = self.database.get_user(user_id)
            if user_data.get('referrer'):
                return
                
            # Ajouter le parrain
            self.database.update_user(user_id, {'referrer': referrer_id})
            
            # Mettre à jour les statistiques du parrain
            referrer_data = self.database.get_user(referrer_id)
            referrals = referrer_data.get('referrals', [])
            referrals.append(user_id)
            self.database.update_user(referrer_id, {'referrals': referrals})
            


            current_balance = referrer_data.get('balance')
            new_balance = current_balance + self.config.REFERRAL_BONUS
            self.database.update_user(referrer_id, {'balance': new_balance})
                
        except ValueError:
            pass
            
    async def show_referral_info(self, update, context):
        """Afficher les informations de parrainage"""
        if update.callback_query:
            query = update.callback_query
            user_id = query.from_user.id
            chat_id = query.message.chat_id
            await query.answer()
        else:
            user_id = update.effective_user.id
            chat_id = update.effective_chat.id
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        referrals_count = len(user_data.get('referrals', []))
        balance = user_data.get('balance')
        
        bot_username = context.bot.username
        referral_link = f"https://t.me/{bot_username}?start={user_id}"
        
        message = self.texts[language]["referral_info"].format(
            referrals_count=referrals_count,
            balance=balance,
            referral_link=referral_link,
            bonus=self.config.REFERRAL_BONUS,
            min_referrals=self.config.MIN_REFERRALS_FOR_BONUS
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                self.texts[language]["back_button"], 
                callback_data="main_menu"
            )]
        ])
        
        if update.callback_query:
            await query.edit_message_text(
                text=message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text=message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )