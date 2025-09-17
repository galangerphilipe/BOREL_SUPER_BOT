from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from core.question import Question
from core.verification import GroupVerification
from core.referral import ReferralSystem
from core.navigation import Navigation
from games.game_manager import GameManager
from utils.database import Database
from config.settings import Config
from core.couponSend import CouponSend
import logging
import signal
import sys

class TelegramBot:
    def __init__(self):
        self.config = Config()
        self.application = Application.builder().token(self.config.BOT_TOKEN).build()
        self.database = Database()
        self.verification = GroupVerification(self.config, self.database)
        self.referral = ReferralSystem(self.config, self.database)
        self.navigation = Navigation(self.config, self.database)
        self.game_manager = GameManager(self.config, self.database)
        self.question_system = Question(self.config, self.database)
        self.coupon_system = CouponSend(self.config, self.database)
        
        self._setup_handlers()
        self._setup_shutdown_handler()

    def _setup_shutdown_handler(self):
        """Configure le gestionnaire d'arrêt propre"""
        def signal_handler(sig, frame):
            logging.info("Signal d'arrêt reçu, arrêt du bot...")
            self.stop()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
    def _setup_handlers(self):
        """Configure tous les handlers du bot"""
        # Commandes de base
        self.application.add_handler(CommandHandler("start", self.start_command))
        
        # Callbacks pour la navigation
        self.application.add_handler(CallbackQueryHandler(
            self.navigation.handle_language_selection, 
            pattern="^(fr|en|ar)$"
        ))
        
        self.application.add_handler(CallbackQueryHandler(
            self.verification.verify_group_membership, 
            pattern="^verify_group$"
        ))
        
        self.application.add_handler(CallbackQueryHandler(
            self.navigation.handle_main_menu, 
            pattern="^main_menu$"
        ))
        
        self.application.add_handler(CallbackQueryHandler(
            self.navigation.handle_back, 
            pattern="^back_.*"
        ))
        
        # Callbacks pour les jeux
        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.show_games_list, 
            pattern="^show_games$"
        ))
        
        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.select_game, 
            pattern="^game_.*"
        ))
        
        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.start_game, 
            pattern="^start_game_.*"
        ))

        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_crash, 
            pattern="^play_crash$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_apple_of_fortune,
            pattern="^play_wheel$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_under_over_7,
            pattern="^play_under_over_7$"
        ))
        
        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_game_of_thrones,
            pattern="^play_game_of_thrones$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_kamikaze,
            pattern="^play_kamikaze$"
        ))

        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_thimbles,
            pattern="^play_thimbles$"
        ))

        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_swamp_land,
            pattern="^play_swamp_land$"
        ))
        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_games_mines,
            pattern="^play_games_mines$"
        ))

        self.application.add_handler(CallbackQueryHandler(
            self.game_manager.handle_play_casino_mines,
            pattern="^play_casino_mines$"
        ))
        # Callbacks pour le parrainage
        self.application.add_handler(CallbackQueryHandler(
            self.referral.show_referral_info, 
            pattern="^referral_info$"
        ))
        
        # Messages texte
        self.application.add_handler(MessageHandler(
            filters.TEXT & ~filters.COMMAND, 
            self.handle_text_message
        ))

        self.application.add_handler(CallbackQueryHandler(
            self.question_system.start_question_process, 
            pattern="^send_question$"
        ))

        self.application.add_handler(CallbackQueryHandler(
            self.question_system.cancel_question, 
            pattern="^cancel_question$"
        ))


        # Handler pour la création de coupon
        self.application.add_handler(CallbackQueryHandler(
            self.coupon_system.start_coupon_creation,
            pattern="^create_coupon$"
        ))
        
        self.application.add_handler(
            MessageHandler(
                filters.TEXT | filters.PHOTO | filters.VIDEO | filters.Document.VIDEO,
                self.coupon_system.handle_coupon_submission
            )
        )
        
    async def start_command(self, update, context):
        """Gestionnaire de la commande /start"""
        user_id = update.effective_user.id
        
        # Vérifier si c'est un lien de parrainage
        if context.args:
            referrer_id = context.args[0]
            await self.referral.handle_referral(user_id, referrer_id)
        await self.verification.require_group_membership(update, context) 
        await self.navigation.show_language_selection(update, context)
        
    async def handle_text_message(self, update, context):
        """Gestionnaire des messages texte"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if not self.verification.is_user_verified(user_id):
            await self.verification.require_group_membership(update, context) 
            return
        
        if self.question_system.is_waiting_for_question(user_id):
            await self.question_system.handle_question_message(update, context)
            return

        if self.game_manager.is_waiting_for_account_id(user_id):
            await self.game_manager.handle_account_id_input(update, context, text)
            return
            
        await self.navigation.handle_menu_selection(update, context, text)
        
    def start(self):
        """Démarrer le bot"""
        try:
            logging.info("🚀 Démarrage du bot...")
            
            # Supprimer le webhook et les mises à jour en attente
            logging.info("🔄 Suppression du webhook...")
            self.application.bot.delete_webhook(drop_pending_updates=True)
            
            logging.info("✅ Bot démarré avec succès - Mode polling")
            self.application.run_polling(
                allowed_updates=["message", "callback_query", "inline_query"],
                drop_pending_updates=True
            )
            
        except Exception as e:
            logging.error(f"❌ Erreur lors du démarrage du bot: {e}")
            raise e
    
    def stop(self):
        """Arrêter le bot proprement"""
        try:
            logging.info("🛑 Arrêt du bot en cours...")
            if self.application:
                self.application.stop()
                logging.info("✅ Bot arrêté avec succès")
        except Exception as e:
            logging.error(f"❌ Erreur lors de l'arrêt du bot: {e}")
            raise e