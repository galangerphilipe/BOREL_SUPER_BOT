import telegram
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, ChatMember
from telegram.ext import ContextTypes
from telegram.error import BadRequest
from utils.helpers import load_texts
from core.navigation import Navigation 

class GroupVerification:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.texts = load_texts()

    def is_user_verified(self, user_id: int) -> bool:
        """Vérifie si l'utilisateur est déjà vérifié."""
        user_data = self.database.get_user(user_id)
        return user_data.get('verified', False)

    async def require_group_membership(self, update, context):
        """Demande à l'utilisateur de rejoindre le groupe avec un bouton de vérification."""
        user_id = update.effective_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')

        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                self.texts[language]["verify_button"],
                callback_data="verify_group"
            )]
        ])
        
        group_link = self.config.TELEGRAM_GROUP
        
        text = self.texts[language]["group_required"].format(
            telegram_group=group_link,
            promo_code=self.config.PROMO_CODE
        )

        if update.message:
            await update.message.reply_text(
                text,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
        elif update.callback_query:
            await update.callback_query.edit_message_text(
                text=text,
                reply_markup=keyboard,
                parse_mode="HTML",
                disable_web_page_preview=True
            )
    
    async def verify_group_membership(self, update, context: ContextTypes.DEFAULT_TYPE):
        """
        Vérifie si l'utilisateur est déjà membre OU s'il a envoyé une demande d'adhésion.
        """
        query = update.callback_query
        await query.answer()

        user_id = query.from_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        group_id = self.config.GROUP_ID

        try:
            member = await context.bot.get_chat_member(chat_id=group_id, user_id=user_id)
            if member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.LEFT, ChatMember.OWNER, ChatMember.RESTRICTED]:
                self.database.update_user(user_id, {'verified': True})
                
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=self.texts[language]["verified"],
                    parse_mode="HTML"
                )
                
                nav = Navigation(self.config, self.database)
                await nav.show_main_menu(update, context)
            else:
                # Ce cas ne devrait presque jamais arriver, sauf pour le statut 'kicked' (banni).
                await context.bot.send_message(
                    chat_id=query.message.chat_id,
                    text=self.texts[language]["not_member"],
                    parse_mode="HTML"
                )

        except BadRequest as e:
            error_message = str(e).lower()
            msg_to_user = self.texts[language]["not_member"]

            if "user not found" in error_message:
                msg_to_user = self.texts[language]["not_member"]
            
            elif "chat not found" in error_message:
                msg_to_user = self.texts[language].get("group_not_found", "❌ Groupe introuvable. Veuillez contacter le support.")
                print(f"Erreur critique : le chat avec l'ID {group_id} est introuvable. Le bot est-il bien administrateur ?")

            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text=msg_to_user,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Une erreur inattendue est survenue : {e}")
            await context.bot.send_message(
                chat_id=query.message.chat_id,
                text="Une erreur est survenue. Veuillez réessayer.",
                parse_mode="HTML"
            )
