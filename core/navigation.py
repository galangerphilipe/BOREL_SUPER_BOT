from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from core.referral import ReferralSystem
from core.tutorials import Tutorial
from utils.helpers import load_texts
from core.couponSend import CouponSend
from games.game_manager import GameManager
from core.question import Question


class Navigation:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.texts = load_texts()
        self.question_system = Question(config, database)
        self.coupon_system = CouponSend(config, database)
        self.tutorial_system = Tutorial(config, database)
        
    async def show_language_selection(self, update, context):
        """Afficher la sélection de langue"""
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton("Français 🇫🇷", callback_data="fr"),
             InlineKeyboardButton("English 🇬🇧", callback_data="en"),
             InlineKeyboardButton("العربية 🇲🇦", callback_data="ar")]
        ])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=self.texts["fr"]["choose_language"],
                reply_markup=keyboard
            )
        else:
            await update.message.reply_text(
                text=self.texts["fr"]["choose_language"],
                reply_markup=keyboard
            )
            
    async def handle_language_selection(self, update, context):
        """Gérer la sélection de langue"""
        query = update.callback_query
        await query.answer()
    
        user_id = query.from_user.id
        language = query.data
    
        # Sauvegarder la langue
        self.database.update_user(user_id, {'language': language})
    
        # Vérifier si l'utilisateur est vérifié
        from core.verification import GroupVerification
        verification = GroupVerification(self.config, self.database)
    
        if verification.is_user_verified(user_id):
            await self.show_main_menu(update, context)
        else:
            await verification.require_group_membership(update, context)

    
    async def show_main_menu(self, update, context):
        """Afficher le menu principal"""
        if hasattr(update, 'callback_query') and update.callback_query:
            user_id = update.callback_query.from_user.id
            query = update.callback_query
        else:
            user_id = update.effective_user.id
            query = None

        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')

        # Menu principal (ReplyKeyboard)
        keyboard = ReplyKeyboardMarkup([
            [
                KeyboardButton(self.texts[language]["how_to_play"]),
                KeyboardButton(self.texts[language]["questions"])
            ],
            [
                KeyboardButton(self.texts[language]["1x_game"]),
                KeyboardButton(self.texts[language]["1win_game"])
            ],
            [
                KeyboardButton(self.texts[language]["referral_menu"]),
                KeyboardButton(self.texts[language]["coupon_brunch"])
            ],
            [
                KeyboardButton(self.texts[language]["change_language"]),
                KeyboardButton("🎥 Vidéo d'inscription")
            ],
        ], resize_keyboard=True)

        # Texte d'accueil
        welcome_text = self.texts[language]["start"].format(
            links=self.config.LINKS,
            promo_code=self.config.PROMO_CODE
        )

        # Envoi du menu principal
        await context.bot.send_message(
            chat_id=user_id,
            text=welcome_text,
            reply_markup=keyboard,
            parse_mode="HTML"
        )

        # Boutons vers les autres bots (InlineKeyboard)
        link_keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton("🎯 Aviator Predictor Bot", url="https://t.me/AviatorPredictor12HackBot")
            ],
            [
                InlineKeyboardButton("💸 Parrainer Pour Gagner", url="https://t.me/ParrainerPourGagner1Bot")
            ]
        ])

        await context.bot.send_message(
            chat_id=user_id,
            text="👇 *Découvre aussi nos autres bots utiles* 👇",
            reply_markup=link_keyboard,
            parse_mode="Markdown"
        )

        # Si appel via un bouton (callback), on marque le query comme traité
        if query:
            await query.answer()
                
    async def handle_main_menu(self, update, context):
        """Retour au menu principal"""
        await self.show_main_menu(update, context)
        
    async def handle_back(self, update, context):
        """Gérer les boutons retour"""
        query = update.callback_query
        await query.answer()
        
        callback_data = query.data
        
        if callback_data == "back_main":
            await self.show_main_menu(update, context)
        elif callback_data == "back_games":
            game_manager = GameManager(self.config, self.database)
            await game_manager.show_games_list(update, context)
    
    async def handle_text_message(self, update, context):
        """Gérer les messages texte (incluant les questions)"""
        user_id = update.effective_user.id
        
        # Vérifier si l'utilisateur est en train d'envoyer une question
        if self.question_system.is_waiting_for_question(user_id):
            await self.question_system.handle_question_message(update, context)
            return
        
        # Sinon, traiter comme une sélection de menu normale
        await self.handle_menu_selection(update, context)
    
    async def handle_menu_selection(self, update, context, text=None):
        """Gérer les sélections du menu principal via texte ou callback"""
        user_id = update.effective_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        # Handle callback query if present
        if update.callback_query:
            query = update.callback_query
            await query.answer()
            text = query.data
        else:
            text = update.message.text

        # Gestion des jeux séparés 1x_game et 1win_game
        if text == self.texts[language]["how_to_play"] or text == "how_to_play":
            await self.tutorial_system.show_tutorial(update, context)
        elif text == self.texts[language]["questions"] or text == "questions":
            await self.question_system.show_question_menu(update, context)
        elif text == "🎥 Vidéo d'inscription" or text == "video_inscription":
            await self.tutorial_system.show_video_inscription(update, context)
        elif text == self.texts[language]["1x_game"] or text == "1x_game":
            game_manager = GameManager(self.config, self.database)
            await game_manager.show_games_list(update, context)
        elif text == self.texts[language]["1win_game"] or text == "1win_game":
            game_manager = GameManager(self.config, self.database)
            await game_manager.show_1win_games_list(update, context)
        elif text == self.texts[language]["referral_menu"] or text == "referral_menu":
            referral = ReferralSystem(self.config, self.database)
            await referral.show_referral_info(update, context)
        elif text == self.texts[language]["coupon_brunch"] or text == "coupon_brunch":
            await self.coupon_system.show_daily_coupons(update, context)
        elif text == self.texts[language]["change_language"] or text == "change_language":
            await self.show_language_selection(update, context)
        else:
            await update.message.reply_text(self.texts[language]["invalid_selection"])
            
    async def handle_callback_query(self, update, context):
        """Gérer les callback queries spécifiques aux questions"""
        query = update.callback_query
        callback_data = query.data
        
        if callback_data == "send_question":
            await self.question_system.start_question_process(update, context)
        elif callback_data == "cancel_question":
            await self.question_system.cancel_question(update, context)
        else:
            # Déléguer aux autres handlers
            await self.handle_menu_selection(update, context)