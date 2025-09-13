from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from utils.helpers import load_texts
import datetime

class Question:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.texts = load_texts()
        self.waiting_for_question = {}  # Dictionnaire pour tracker les utilisateurs en attente
        
    async def show_question_menu(self, update, context):
        """Afficher le menu des questions"""
        user_id = update.effective_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                self.texts[language]["send_question"], 
                callback_data="send_question"
            )],
            [InlineKeyboardButton(
                self.texts[language]["back_main"], 
                callback_data="back_main"
            )]
        ])
        
        if update.callback_query:
            await update.callback_query.edit_message_text(
                text=self.texts[language]["questions_menu"],
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        else:
            await update.message.reply_text(
                text=self.texts[language]["questions_menu"],
                reply_markup=keyboard,
                parse_mode="HTML"
            )
    
    async def start_question_process(self, update, context):
        """Démarrer le processus d'envoi de question"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        # Marquer l'utilisateur comme en attente d'une question
        self.waiting_for_question[user_id] = True
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                self.texts[language]["cancel"], 
                callback_data="cancel_question"
            )]
        ])
        
        await query.edit_message_text(
            text=self.texts[language]["ask_question_prompt"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
    
    async def handle_question_message(self, update, context):
        """Gérer le message de question de l'utilisateur"""
        user_id = update.effective_user.id
        
        # Vérifier si l'utilisateur est en attente d'une question
        if user_id not in self.waiting_for_question:
            return False
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        question_text = update.message.text
        user_info = update.effective_user
        
        # Envoyer la question à l'admin
        await self.send_question_to_admin(context, user_info, question_text, language)
        
        # Confirmer à l'utilisateur
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                self.texts[language]["back_main"], 
                callback_data="back_main"
            )]
        ])
        
        await update.message.reply_text(
            text=self.texts[language]["question_sent_confirmation"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
        # Retirer l'utilisateur de la liste d'attente
        del self.waiting_for_question[user_id]
        
        return True
    
    async def send_question_to_admin(self, context, user_info, question_text, user_language):
        """Envoyer la question à l'admin"""
        admin_id = self.config.ADMIN_ID
        
        # Créer le message pour l'admin
        current_time = datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        
        admin_message = (
            f"📩 <b>Nouvelle question reçue</b>\n\n"
            f"👤 <b>De:</b> {user_info.first_name}"
        )
        
        if user_info.username:
            admin_message += f" (@{user_info.username})"
        
        admin_message += (
            f"\n🆔 <b>ID:</b> <code>{user_info.id}</code>\n"
            f"🌐 <b>Langue:</b> {user_language.upper()}\n"
            f"⏰ <b>Date:</b> {current_time}\n\n"
            f"💬 <b>Question:</b>\n{question_text}"
        )
        
        # Keyboard pour répondre
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                f"✉️ Répondre à {user_info.first_name}", 
                callback_data=f"reply_to_{user_info.id}"
            )]
        ])
        
        try:
            await context.bot.send_message(
                chat_id=admin_id,
                text=admin_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Erreur lors de l'envoi du message à l'admin: {e}")
    
    async def cancel_question(self, update, context):
        """Annuler l'envoi de question"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        # Retirer l'utilisateur de la liste d'attente
        if user_id in self.waiting_for_question:
            del self.waiting_for_question[user_id]
        
        # Retourner au menu des questions
        await self.show_question_menu(update, context)
    
    def is_waiting_for_question(self, user_id):
        """Vérifier si un utilisateur est en attente d'une question"""
        return user_id in self.waiting_for_question