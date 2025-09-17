import logging
import os
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters
from config.settings import Config
from core.couponSend import CouponSend
from core.navigation import Navigation
from core.question import Question
from core.referral import ReferralSystem
from core.verification import GroupVerification
from games.game_manager import GameManager
from utils.database import Database

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger()

# Importer keep_alive seulement si nécessaire
try:
    from keep_alive import keep_alive
    keep_alive()
    logger.info("✅ Keep-alive activé")
except ImportError:
    logger.warning("⚠️ Keep-alive non disponible")

if __name__ == "__main__":
    config = Config()
    db = Database()
    app = Application.builder().token(config.BOT_TOKEN).build()
    verification = GroupVerification(config, db)
    referral = ReferralSystem(config, db)
    navigation = Navigation(config, db)
    game_manager = GameManager(config, db)
    question_system = Question(config, db)
    coupon_system = CouponSend(config, db)

    async def start_command(update, context):
        """Gestionnaire de la commande /start"""
        user_id = update.effective_user.id
        
        # Vérifier si c'est un lien de parrainage
        if context.args:
            referrer_id = context.args[0]
            await referral.handle_referral(user_id, referrer_id)
        await verification.require_group_membership(update, context) 
        await navigation.show_language_selection(update, context)
        
    async def handle_text_message(update, context):
        """Gestionnaire des messages texte"""
        user_id = update.effective_user.id
        text = update.message.text
        
        if not verification.is_user_verified(user_id):
            await verification.require_group_membership(update, context) 
            return
        
        # Vérifier d'abord si l'utilisateur attend d'envoyer un coupon (admin seulement)
        user_data = db.get_user(user_id)
        if user_data.get('waiting_for_coupon', False) and str(user_id) == str(config.ADMIN_ID):
            await coupon_system.handle_coupon_submission(update, context)
            return
        
        if question_system.is_waiting_for_question(user_id):
            await question_system.handle_question_message(update, context)
            return

        if game_manager.is_waiting_for_account_id(user_id):
            await game_manager.handle_account_id_input(update, context, text)
            return
            
        await navigation.handle_menu_selection(update, context, text)

    async def handle_media_message(update, context):
        """Gestionnaire spécifique pour les messages média (photo/vidéo)"""
        user_id = update.effective_user.id
        
        if not verification.is_user_verified(user_id):
            await verification.require_group_membership(update, context) 
            return
        
        # Vérifier si l'admin est en train d'envoyer un coupon
        user_data = db.get_user(user_id)
        if user_data.get('waiting_for_coupon', False) and str(user_id) == str(config.ADMIN_ID):
            await coupon_system.handle_coupon_submission(update, context)
            return
        
        # Sinon, message média non attendu
        await update.message.reply_text("Je ne sais pas quoi faire de ce fichier. Utilisez le menu pour naviguer.")

    # Handlers de commandes
    app.add_handler(CommandHandler("start", start_command))
    
    # Callbacks pour la navigation
    app.add_handler(CallbackQueryHandler(navigation.handle_language_selection, pattern="^(fr|en|ar)$"))
    app.add_handler(CallbackQueryHandler(verification.verify_group_membership, pattern="^verify_group$"))
    app.add_handler(CallbackQueryHandler(navigation.handle_main_menu, pattern="^main_menu$"))
    app.add_handler(CallbackQueryHandler(navigation.handle_back, pattern="^back_.*"))
    
    # Callbacks pour les jeux
    app.add_handler(CallbackQueryHandler(game_manager.show_games_list, pattern="^show_games$"))
    app.add_handler(CallbackQueryHandler(game_manager.select_game, pattern="^game_.*"))
    app.add_handler(CallbackQueryHandler(game_manager.start_game, pattern="^start_game_.*"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_crash, pattern="^play_crash$"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_apple_of_fortune, pattern="^play_wheel$"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_under_over_7, pattern="^play_under_over_7$"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_game_of_thrones, pattern="^play_game_of_thrones$"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_kamikaze, pattern="^play_kamikaze$"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_thimbles, pattern="^play_thimbles$"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_swamp_land, pattern="^play_swamp_land$"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_games_mines, pattern="^play_games_mines$"))
    app.add_handler(CallbackQueryHandler(game_manager.handle_play_casino_mines, pattern="^play_casino_mines$"))
    
    # Callbacks pour le parrainage
    app.add_handler(CallbackQueryHandler(referral.show_referral_info, pattern="^referral_info$"))
    
    # Callbacks pour les questions
    app.add_handler(CallbackQueryHandler(question_system.start_question_process, pattern="^send_question$"))
    app.add_handler(CallbackQueryHandler(question_system.cancel_question, pattern="^cancel_question$"))
    
    # Handler pour la création de coupon
    app.add_handler(CallbackQueryHandler(coupon_system.start_coupon_creation, pattern="^create_coupon$"))
    
    # Handler pour les messages texte (doit être après les callbacks)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    
    # Handler séparé pour les médias (photo/vidéo)
    app.add_handler(MessageHandler(filters.PHOTO | filters.VIDEO | filters.Document.VIDEO, handle_media_message))

    logger.info("🚀 Bot is running...")
    app.run_polling(poll_interval=5)