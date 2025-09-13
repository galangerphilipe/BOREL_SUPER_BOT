import os
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

class Tutorial:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.texts = self._load_texts()
        self.tutorial_image_path = "media/tutorials/tutorials.jpg"
        self.tutorials_video_path = "media/tutorials/tutorials.mp4"

    def _load_texts(self):
        from utils.helpers import load_texts
        return load_texts()

    async def show_tutorial(self, update, context):
        """Afficher le tutoriel avec image et texte formaté"""
        if hasattr(update, 'callback_query') and update.callback_query:
            user_id = update.callback_query.from_user.id
            query = update.callback_query
        else:
            user_id = update.effective_user.id
            query = None

        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')

        # Formatage du texte avec les données de config
        tutorial_text = self.texts[language]["how_to_play_text"].format(
            promo_code=self.config.PROMO_CODE,
            xbet_link=self.config.LINKS.get('1xbet', 'https://urls.fr/j0C9yU'),
            betwinne_link=self.config.LINKS.get('betwinne', 'https://bwredir.com/2qUY?p=%2Fregistration%2F'),
            melbet_link=self.config.LINKS.get('melbet', 'https://refpakrtsb.top/L?tag=d_4475033m_45415c_&site=4475033&ad=45415'),
            winwin_link=self.config.LINKS.get('winwin', 'https://refpa443273.top/L?tag=d_4440428m_64485c_&site=4440428&ad=64485')
        )

        # Bouton de retour
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                self.texts[language]["back_button"],
                callback_data="back_main"
            )
        ]])

        try:
            # Envoyer l'image d'abord (si elle existe)
            if os.path.exists(self.tutorial_image_path):
                with open(self.tutorial_image_path, 'rb') as img_file:
                    if query:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=img_file,
                            caption="📚 GUIDE D'INSCRIPTION 📚"
                        )
                        await query.answer()
                    else:
                        await update.message.reply_photo(
                            photo=img_file,
                            caption="📚 GUIDE D'INSCRIPTION 📚"
                        )

            # Puis envoyer le texte séparément
            if query:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=tutorial_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    text=tutorial_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )

        except Exception as e:
            print(f"Erreur lors de l'envoi du tutoriel: {e}")
            # En cas d'erreur, envoyer au moins le texte
            error_text = self.texts[language]["tutorial_error"]
            if query:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=error_text,
                    reply_markup=keyboard
                )
                if not query.message.from_user.is_bot:
                    await query.answer()
            else:
                await update.message.reply_text(
                    text=error_text,
                    reply_markup=keyboard
                )

    async def show_video_inscription(self, update, context):
        """Afficher la vidéo d'inscription avec texte formaté"""
        if hasattr(update, 'callback_query') and update.callback_query:
            user_id = update.callback_query.from_user.id
            query = update.callback_query
        else:
            user_id = update.effective_user.id
            query = None

        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')

        # Formatage du texte avec les données de config
        video_text = self.texts[language]["video_inscription"].format(
            promo_code=self.config.PROMO_CODE,
            xbet_link=self.config.LINKS.get('1xbet', 'https://urls.fr/j0C9yU'),
            betwinne_link=self.config.LINKS.get('betwinne', 'https://bwredir.com/2qUY?p=%2Fregistration%2F'),
            melbet_link=self.config.LINKS.get('melbet', 'https://refpakrtsb.top/L?tag=d_4475033m_45415c_&site=4475033&ad=45415'),
            winwin_link=self.config.LINKS.get('winwin', 'https://refpa443273.top/L?tag=d_4440428m_64485c_&site=4440428&ad=64485'),
            megapari_link=self.config.LINKS.get('megapari', 'https://refpaiozdg.top/L?tag=d_3160465m_25437c_&site=3160465&ad=25437&r=registration')
        )

        # Bouton de retour
        keyboard = InlineKeyboardMarkup([[
            InlineKeyboardButton(
                self.texts[language]["back_button"],
                callback_data="back_main"
            )
        ]])

        try:

            # Puis envoyer le texte séparément
            if query:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=video_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            else:
                await update.message.reply_text(
                    text=video_text,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            
            # Envoyer la vidéo d'abord (si elle existe)
            if os.path.exists(self.tutorials_video_path):
                with open(self.tutorials_video_path, 'rb') as video_file:
                    if query:
                        await context.bot.send_video(
                            chat_id=user_id,
                            video=video_file,
                            caption="📹VIDÉO D'INSCRIPTION 📹"
                        )
                        await query.answer()
                    else:
                        await update.message.reply_video(
                            video=video_file,
                            caption="📹 VIDÉO D'INSCRIPTION📹"
                        )

        except Exception as e:
            print(f"Erreur lors de l'envoi de la vidéo d'inscription: {e}")
            # En cas d'erreur, envoyer au moins le texte
            error_text = self.texts[language]["tutorial_error"]
            if query:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=error_text,
                    reply_markup=keyboard
                )
                if not query.message.from_user.is_bot:
                    await query.answer()
            else:
                await update.message.reply_text(
                    text=error_text,
                    reply_markup=keyboard
                )