from datetime import datetime, date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, File
import os
import asyncio

class CouponSend:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.texts = self._load_texts()
        self.media_path = "media/coupons"
        os.makedirs(self.media_path, exist_ok=True)

    def _load_texts(self):
        # Cette fonction doit charger tes textes multilingues (à adapter si besoin)
        from utils.helpers import load_texts
        return load_texts()

    async def start_coupon_creation(self, update, context):
        """Lancer la création de coupon par l'admin"""
        user_id = update.effective_user.id
        if str(user_id) != str(self.config.ADMIN_ID):
            await update.callback_query.answer(self.texts['fr']['not_admin'])
            return

        self.database.update_user(user_id, {'waiting_for_coupon': True})

        await update.callback_query.message.reply_text(
            self.texts['fr']['send_coupon_prompt']
        )
        await update.callback_query.answer()

    async def start_announcement_creation(self, update, context):
        """Lancer la création d'annonce par l'admin"""
        user_id = update.effective_user.id
        if str(user_id) != str(self.config.ADMIN_ID):
            await update.callback_query.answer(self.texts['fr']['not_admin'])
            return

        self.database.update_user(user_id, {'waiting_for_announcement': True})

        await update.callback_query.message.reply_text(
            self.texts['fr']['send_announcement_prompt']
        )
        await update.callback_query.answer()

    async def handle_coupon_submission(self, update, context):
        """Gérer l'envoi d'un coupon par l'admin et le diffuser automatiquement"""
        user_id = update.effective_user.id
        message = update.message

        user_data = self.database.get_user(user_id)
        if str(user_id) != str(self.config.ADMIN_ID) or not user_data.get('waiting_for_coupon', False):
            await message.reply_text(self.texts['fr']['not_admin'])
            return

        if not message.photo:
            await message.reply_text(self.texts['fr']['invalid_coupon'])
            return

        # Télécharger l'image
        photo = message.photo[-1]
        tg_file: File = await context.bot.get_file(photo.file_id)

        file_extension = os.path.splitext(tg_file.file_path)[1] or ".jpg"
        file_name = f"coupon_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
        file_path = os.path.join(self.media_path, file_name)

        await tg_file.download_to_drive(custom_path=file_path)

        coupon_data = {
            'coupon_id': f"coupon_{datetime.now().isoformat()}",
            'text': message.caption or "",
            'photo_path': file_path,
            'created_at': datetime.now().isoformat(),
            'date': date.today().isoformat(),
            'admin_id': user_id
        }

        # Sauvegarder le coupon
        self.database.add_coupon(coupon_data)
        self.database.update_user(user_id, {'waiting_for_coupon': False})

        # Confirmer à l'admin
        await message.reply_text(self.texts['fr']['coupon_added'])

        # Diffuser automatiquement le coupon à tous les utilisateurs
        await self.broadcast_coupon(context, coupon_data)

    async def handle_announcement_submission(self, update, context):
        """Gérer l'envoi d'une annonce par l'admin et la diffuser immédiatement"""
        user_id = update.effective_user.id
        message = update.message

        user_data = self.database.get_user(user_id)
        if str(user_id) != str(self.config.ADMIN_ID) or not user_data.get('waiting_for_announcement', False):
            await message.reply_text(self.texts['fr']['not_admin'])
            return

        self.database.update_user(user_id, {'waiting_for_announcement': False})

        # Confirmer à l'admin
        await message.reply_text(self.texts['fr']['announcement_sent'])

        # Diffuser immédiatement l'annonce à tous les utilisateurs
        await self.broadcast_announcement(context, message)

    async def broadcast_coupon(self, context, coupon_data):
        """Diffuser un coupon à tous les utilisateurs du bot"""
        all_users = self.database.get_all_users()  # Retourne le dictionnaire des utilisateurs
        
        caption = f"🎟️ **NOUVEAU COUPON** 🎟️\n\n📌 {coupon_data['text']}\n🕒 {coupon_data['created_at']}"
        
        success_count = 0
        failed_count = 0
        
        # Itérer sur les valeurs du dictionnaire (les objets utilisateur)
        for user_id, user_data in all_users.items():
            try:
                # user_id est déjà la clé (ID de l'utilisateur)
                if user_id and str(user_id) != str(self.config.ADMIN_ID):  # Ne pas envoyer à l'admin
                    if coupon_data.get('photo_path') and os.path.exists(coupon_data['photo_path']):
                        with open(coupon_data['photo_path'], 'rb') as img_file:
                            await context.bot.send_photo(
                                chat_id=int(user_id),  # Convertir en int pour Telegram
                                photo=img_file,
                                caption=caption,
                                parse_mode="Markdown"
                            )
                    else:
                        await context.bot.send_message(
                            chat_id=int(user_id),  # Convertir en int pour Telegram
                            text=caption,
                            parse_mode="Markdown"
                        )
                    success_count += 1
                    # Petite pause pour éviter le rate limiting
                    await asyncio.sleep(0.1)
            except Exception as e:
                failed_count += 1
                print(f"Erreur envoi coupon à {user_id}: {e}")
                # Continue la boucle même en cas d'erreur (utilisateur bloqué, etc.)
                continue
        
        # Notifier l'admin du résultat
        await context.bot.send_message(
            chat_id=self.config.ADMIN_ID,
            text=f"📊 **Diffusion du coupon terminée**\n\n✅ Envoyé avec succès: {success_count}\n❌ Échecs: {failed_count}",
            parse_mode="Markdown"
        )

    async def broadcast_announcement(self, context, message):
        """Diffuser une annonce à tous les utilisateurs du bot"""
        all_users = self.database.get_all_users()  # Retourne le dictionnaire des utilisateurs
        
        success_count = 0
        failed_count = 0
        
        # Itérer sur les valeurs du dictionnaire (les objets utilisateur)
        for user_id, user_data in all_users.items():
            try:
                # user_id est déjà la clé (ID de l'utilisateur)
                if user_id and str(user_id) != str(self.config.ADMIN_ID):  # Ne pas envoyer à l'admin
                    if message.photo:
                        # Annonce avec image
                        photo = message.photo[-1]
                        caption = f"📢 **ANNONCE OFFICIELLE** 📢\n\n{message.caption or ''}"
                        await context.bot.send_photo(
                            chat_id=int(user_id),  # Convertir en int pour Telegram
                            photo=photo.file_id,
                            caption=caption,
                            parse_mode="Markdown"
                        )
                    else:
                        # Annonce texte seulement
                        announcement_text = f"📢 **ANNONCE OFFICIELLE** 📢\n\n{message.text}"
                        await context.bot.send_message(
                            chat_id=int(user_id),  # Convertir en int pour Telegram
                            text=announcement_text,
                            parse_mode="Markdown"
                        )
                    success_count += 1
                    # Petite pause pour éviter le rate limiting
                    await asyncio.sleep(0.1)
            except Exception as e:
                failed_count += 1
                print(f"Erreur envoi annonce à {user_id}: {e}")
                # Continue la boucle même en cas d'erreur (utilisateur bloqué, etc.)
                continue
        
        # Notifier l'admin du résultat
        await context.bot.send_message(
            chat_id=self.config.ADMIN_ID,
            text=f"📊 **Diffusion de l'annonce terminée**\n\n✅ Envoyé avec succès: {success_count}\n❌ Échecs: {failed_count}",
            parse_mode="Markdown"
        )

    async def show_daily_coupons(self, update, context):
        """Afficher chaque coupon du jour séparément (image + texte)"""
        user_id = update.effective_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')

        today = date.today().isoformat()
        coupons = self.database.get_daily_coupons(today)

        # Cas : aucun coupon pour un utilisateur normal
        if not coupons and str(user_id) != str(self.config.ADMIN_ID):
            await context.bot.send_message(
                chat_id=user_id,
                text=self.texts[language]['daily_coupons_header'] + "\n\n" + self.texts[language]['no_coupons'],
                reply_markup=InlineKeyboardMarkup([[
                    InlineKeyboardButton(
                        self.texts[language]['back_button'],
                        callback_data='back_main'
                    )
                ]])
            )
            return

        # Cas : aucun coupon pour l'admin
        if str(user_id) == str(self.config.ADMIN_ID) and not coupons:
            keyboard = [
                [
                    InlineKeyboardButton(
                        self.texts[language]['create_coupon'],
                        callback_data='create_coupon'
                    ),
                ],
                [
                    InlineKeyboardButton(
                        self.texts[language]['back_button'],
                        callback_data='back_main'
                    )
                ]
            ]
            await context.bot.send_message(
                chat_id=user_id,
                text=self.texts[language]['daily_coupons_header'] + "\n\n" + self.texts[language]['no_coupons'],
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
            return

        # Envoyer chaque coupon un par un
        for coupon in coupons:
            caption = f"📌 {coupon['text']}\n🕒 {coupon['created_at']}"
            if coupon.get('photo_path') and os.path.exists(coupon['photo_path']):
                with open(coupon['photo_path'], 'rb') as img_file:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=img_file,
                        caption=caption
                    )
            else:
                await context.bot.send_message(
                    chat_id=user_id,
                    text=caption
                )

        # Ajouter un dernier message avec les boutons de navigation
        keyboard = [[
            InlineKeyboardButton(
                self.texts[language]['back_button'],
                callback_data='back_main'
            )
        ]]

        if str(user_id) == str(self.config.ADMIN_ID):
            keyboard.insert(0, [
                InlineKeyboardButton(
                    self.texts[language]['create_coupon'],
                    callback_data='create_coupon'
                ),
            ])

        await context.bot.send_message(
            chat_id=user_id,
            text="✅ " + self.texts[language]['daily_coupons_header'] + " - fin de la liste",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )