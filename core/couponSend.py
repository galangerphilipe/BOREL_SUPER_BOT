from datetime import datetime, date
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, File
from telegram.error import TelegramError, Forbidden, BadRequest
import os
import asyncio
import logging

logger = logging.getLogger(__name__)

class CouponSend:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.texts = self._load_texts()
        self.media_path = "media/coupons"
        os.makedirs(self.media_path, exist_ok=True)
        
        self.batch_size = 30  # Taille des batches pour l'envoi
        self.batch_delay = 1.0  # Délai entre les batches en secondes
        self.send_delay = 0.03  # Délai minimal entre les envois individuels
        self.max_retries = 2  # Nombre de tentatives maximum
        
        # Limites Telegram
        self.MAX_VIDEO_SIZE = 50 * 1024 * 1024  # 50 MB
        self.MAX_PHOTO_SIZE = 10 * 1024 * 1024  # 10 MB
        
        # Formats supportés
        self.SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv', '.webm']
        self.SUPPORTED_PHOTO_FORMATS = ['.jpg', '.jpeg', '.png', '.webp']

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
            self.texts['fr']['send_coupon_prompt'] + 
            "\n\n📝 **Formats supportés:**\n" +
            "🖼️ Images: JPG, PNG, WEBP (max 10MB)\n" +
            "🎥 Vidéos: MP4, AVI, MOV, MKV, WEBM (max 50MB)\n" +
            "📄 Texte: Messages texte simples",
            parse_mode="Markdown"
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

        # Déterminer le type de contenu
        media_type = None
        file_id = None
        file_path = None
        file_size = 0

        if message.photo:
            media_type = "photo"
            file_id = message.photo[-1].file_id  # Prendre la plus haute résolution
            file_size = message.photo[-1].file_size or 0
        elif message.video:
            media_type = "video"
            file_id = message.video.file_id
            file_size = message.video.file_size or 0
        elif message.document and message.document.mime_type:
            # Vérifier si c'est une vidéo envoyée comme document
            mime_type = message.document.mime_type.lower()
            if mime_type.startswith('video/'):
                media_type = "video"
                file_id = message.document.file_id
                file_size = message.document.file_size or 0
            elif mime_type.startswith('image/'):
                media_type = "photo"
                file_id = message.document.file_id
                file_size = message.document.file_size or 0
        elif message.text or message.caption:
            media_type = "text"
        else:
            await message.reply_text(
                "❌ **Format non supporté**\n\n" +
                "Formats acceptés:\n" +
                "🖼️ Images: JPG, PNG, WEBP\n" +
                "🎥 Vidéos: MP4, AVI, MOV, MKV, WEBM\n" +
                "📄 Texte simple",
                parse_mode="Markdown"
            )
            return

        # Vérifier la taille du fichier
        if media_type == "photo" and file_size > self.MAX_PHOTO_SIZE:
            await message.reply_text(
                f"❌ **Image trop volumineuse**\n\n" +
                f"Taille actuelle: {file_size/1024/1024:.1f} MB\n" +
                f"Limite: {self.MAX_PHOTO_SIZE/1024/1024:.0f} MB",
                parse_mode="Markdown"
            )
            return
        elif media_type == "video" and file_size > self.MAX_VIDEO_SIZE:
            await message.reply_text(
                f"❌ **Vidéo trop volumineuse**\n\n" +
                f"Taille actuelle: {file_size/1024/1024:.1f} MB\n" +
                f"Limite: {self.MAX_VIDEO_SIZE/1024/1024:.0f} MB",
                parse_mode="Markdown"
            )
            return

        try:
            # Télécharger le fichier média si c'est une image ou vidéo
            if media_type in ["photo", "video"]:
                tg_file: File = await context.bot.get_file(file_id)
                
                # Déterminer l'extension selon le type
                if media_type == "photo":
                    file_extension = os.path.splitext(tg_file.file_path)[1] or ".jpg"
                    file_name = f"coupon_photo_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
                else:  # video
                    file_extension = os.path.splitext(tg_file.file_path)[1] or ".mp4"
                    file_name = f"coupon_video_{datetime.now().strftime('%Y%m%d_%H%M%S')}{file_extension}"
                
                file_path = os.path.join(self.media_path, file_name)
                
                # Message de progression pour les gros fichiers
                if file_size > 5 * 1024 * 1024:  # > 5MB
                    progress_msg = await message.reply_text(
                        f"⬇️ **Téléchargement en cours...**\n" +
                        f"Fichier: {file_size/1024/1024:.1f} MB",
                        parse_mode="Markdown"
                    )
                
                await tg_file.download_to_drive(custom_path=file_path)
                
                # Supprimer le message de progression
                if file_size > 5 * 1024 * 1024:
                    try:
                        await progress_msg.delete()
                    except:
                        pass

            # Valeurs par défaut pour les vidéos (sans traitement CV2)
            video_duration = 30 if media_type == "video" else None  # Valeur par défaut
            video_width = 1280 if media_type == "video" else None   # Valeur par défaut
            video_height = 720 if media_type == "video" else None  # Valeur par défaut

            coupon_data = {
                'coupon_id': f"coupon_{datetime.now().isoformat()}",
                'text': message.caption or message.text or "",
                'media_type': media_type,
                'photo_path': file_path if media_type == "photo" else None,
                'video_path': file_path if media_type == "video" else None,
                'video_duration': video_duration,
                'video_width': video_width,
                'video_height': video_height,
                'thumbnail_path': None,  # Plus de miniatures générées
                'file_size': file_size,
                'created_at': datetime.now().isoformat(),
                'date': date.today().isoformat(),
                'admin_id': user_id
            }

            # Sauvegarder le coupon
            self.database.add_coupon(coupon_data)
            self.database.update_user(user_id, {'waiting_for_coupon': False})

            # Confirmer à l'admin
            confirm_msg = f"✅ **Coupon créé avec succès!**\n\n"
            if media_type == "photo":
                confirm_msg += f"🖼️ **Type:** Image\n📏 **Taille:** {file_size/1024:.0f} KB"
            elif media_type == "video":
                confirm_msg += f"🎥 **Type:** Vidéo\n"
                confirm_msg += f"📏 **Taille:** {file_size/1024/1024:.1f} MB\n"
                confirm_msg += f"⏱️ **Durée:** {video_duration}s (défaut)\n"
                confirm_msg += f"📐 **Résolution:** {video_width}x{video_height} (défaut)"
            else:
                confirm_msg += f"📝 **Type:** Texte"

            await message.reply_text(confirm_msg, parse_mode="Markdown")

            # Obtenir le nombre d'utilisateurs pour estimation
            user_count = self.database.get_user_count()
            estimated_time = (user_count // self.batch_size) * self.batch_delay
            
            # Emoji selon le type de média
            if media_type == "photo":
                media_emoji = "🖼️"
                media_name = "Image"
            elif media_type == "video":
                media_emoji = "🎥"
                media_name = "Vidéo"
            else:
                media_emoji = "📝"
                media_name = "Texte"
            
            await message.reply_text(
                f"🚀 **Diffusion en cours...**\n\n"
                f"{media_emoji} **Type:** {media_name}\n"
                f"👥 Utilisateurs à contacter: {user_count}\n"
                f"⏱️ Temps estimé: {estimated_time:.0f} secondes\n\n"
                f"📊 Vous recevrez un rapport détaillé à la fin.",
                parse_mode="Markdown"
            )

            # Diffuser automatiquement le coupon à tous les utilisateurs
            await self.broadcast_coupon_optimized(context, coupon_data)

        except Exception as e:
            logger.error(f"Erreur lors de la création du coupon: {e}")
            await message.reply_text(
                f"❌ **Erreur lors de la création du coupon:**\n{str(e)}"
            )

    async def _send_coupon_to_user(self, context, user_id, coupon_data, caption):
        """Envoyer un coupon à un utilisateur spécifique avec gestion d'erreur améliorée"""
        try:
            user_id_int = int(user_id)
            
            # Ne pas envoyer à l'admin
            if str(user_id) == str(self.config.ADMIN_ID):
                return {'status': 'skipped', 'reason': 'admin'}

            media_type = coupon_data.get('media_type', 'text')

            if media_type == "photo" and coupon_data.get('photo_path') and os.path.exists(coupon_data['photo_path']):
                with open(coupon_data['photo_path'], 'rb') as img_file:
                    await context.bot.send_photo(
                        chat_id=user_id_int,
                        photo=img_file,
                        caption=caption,
                        parse_mode="Markdown"
                    )
            elif media_type == "video" and coupon_data.get('video_path') and os.path.exists(coupon_data['video_path']):
                # Paramètres pour l'envoi de vidéo
                video_kwargs = {
                    'chat_id': user_id_int,
                    'caption': caption,
                    'parse_mode': "Markdown"
                }
                
                # Ajouter les métadonnées par défaut
                if coupon_data.get('video_duration'):
                    video_kwargs['duration'] = coupon_data['video_duration']
                if coupon_data.get('video_width'):
                    video_kwargs['width'] = coupon_data['video_width']
                if coupon_data.get('video_height'):
                    video_kwargs['height'] = coupon_data['video_height']
                
                # Envoyer la vidéo sans miniature
                with open(coupon_data['video_path'], 'rb') as video_file:
                    video_kwargs['video'] = video_file
                    await context.bot.send_video(**video_kwargs)
            else:
                # Texte simple ou fichier média introuvable
                await context.bot.send_message(
                    chat_id=user_id_int,
                    text=caption,
                    parse_mode="Markdown"
                )
            
            return {'status': 'success'}
            
        except Forbidden:
            # Utilisateur a bloqué le bot
            return {'status': 'blocked', 'error': 'User blocked the bot'}
        except BadRequest as e:
            # Chat non trouvé ou autre erreur BadRequest
            error_msg = str(e).lower()
            if 'file too big' in error_msg or 'request entity too large' in error_msg:
                return {'status': 'file_too_large', 'error': 'File exceeds size limit'}
            elif 'unsupported file format' in error_msg:
                return {'status': 'unsupported_format', 'error': 'Unsupported file format'}
            else:
                return {'status': 'bad_request', 'error': str(e)}
        except TelegramError as e:
            # Autres erreurs Telegram
            return {'status': 'telegram_error', 'error': str(e)}
        except Exception as e:
            # Erreurs générales
            logger.error(f"Erreur inattendue pour l'utilisateur {user_id}: {e}")
            return {'status': 'error', 'error': str(e)}

    async def broadcast_coupon_optimized(self, context, coupon_data):
        """Diffuser un coupon à tous les utilisateurs avec optimisation par batch"""
        start_time = datetime.now()
        
        try:
            # Récupérer tous les utilisateurs
            all_users = self.database.get_all_users()
            user_ids = list(all_users.keys())
            
            if not user_ids:
                await context.bot.send_message(
                    chat_id=self.config.ADMIN_ID,
                    text="⚠️ Aucun utilisateur trouvé dans la base de données."
                )
                return

            # Préparer le message selon le type de média
            media_type = coupon_data.get('media_type', 'text')
            if media_type == "photo":
                emoji = "🖼️"
            elif media_type == "video":
                emoji = "🎥"
            else:
                emoji = "📝"

            caption = (
                f"{emoji} **NOUVELLE ANNONCE** {emoji}\n\n"
                f"📌 {coupon_data['text']}\n"
                f"🕒 {datetime.fromisoformat(coupon_data['created_at']).strftime('%d/%m/%Y à %H:%M')}"
            )

            # Statistiques étendues
            stats = {
                'success': 0,
                'blocked': 0,
                'bad_request': 0,
                'file_too_large': 0,
                'unsupported_format': 0,
                'telegram_error': 0,
                'error': 0,
                'skipped': 0
            }

            total_users = len(user_ids)
            processed_users = 0

            # Traitement par batches
            for i in range(0, len(user_ids), self.batch_size):
                batch_user_ids = user_ids[i:i + self.batch_size]
                
                # Créer les tâches pour ce batch
                tasks = []
                for user_id in batch_user_ids:
                    task = self._send_coupon_to_user(context, user_id, coupon_data, caption)
                    tasks.append(task)
                    await asyncio.sleep(self.send_delay)  # Délai minimal entre créations de tâches

                # Exécuter le batch en parallèle
                try:
                    results = await asyncio.gather(*tasks, return_exceptions=True)
                    
                    # Traiter les résultats
                    for result in results:
                        processed_users += 1
                        
                        if isinstance(result, Exception):
                            stats['error'] += 1
                            logger.error(f"Exception dans le batch: {result}")
                        else:
                            stats[result['status']] += 1

                    # Mettre à jour l'admin sur le progrès (tous les 5 batches)
                    if (i // self.batch_size) % 5 == 0:
                        progress = (processed_users / total_users) * 100
                        await context.bot.send_message(
                            chat_id=self.config.ADMIN_ID,
                            text=f"📈 **Progression: {progress:.1f}%**\n"
                                 f"Traité: {processed_users}/{total_users}",
                            parse_mode="Markdown"
                        )

                    # Pause entre les batches
                    if i + self.batch_size < len(user_ids):
                        await asyncio.sleep(self.batch_delay)

                except Exception as e:
                    logger.error(f"Erreur dans le batch {i//self.batch_size}: {e}")
                    stats['error'] += len(batch_user_ids)

            # Calcul du temps total
            end_time = datetime.now()
            total_time = (end_time - start_time).total_seconds()

            # Rapport final détaillé avec nouvelles statistiques
            report = (
                f"📊 **RAPPORT DE DIFFUSION**\n\n"
                f"⏰ **Durée totale:** {total_time:.1f} secondes\n"
                f"👥 **Total utilisateurs:** {total_users}\n\n"
                f"✅ **Envoyés avec succès:** {stats['success']}\n"
                f"🚫 **Utilisateurs ayant bloqué le bot:** {stats['blocked']}\n"
                f"⚠️ **Erreurs de requête:** {stats['bad_request']}\n"
                f"📦 **Fichier trop volumineux:** {stats['file_too_large']}\n"
                f"🎬 **Format non supporté:** {stats['unsupported_format']}\n"
                f"🌐 **Erreurs Telegram:** {stats['telegram_error']}\n"
                f"❌ **Autres erreurs:** {stats['error']}\n"
                f"⏭️ **Ignorés (admin):** {stats['skipped']}\n\n"
                f"📈 **Taux de réussite:** {(stats['success']/(total_users-stats['skipped'])*100):.1f}%\n"
                f"⚡ **Vitesse moyenne:** {(total_users/total_time):.1f} utilisateurs/seconde"
            )

            # Envoyer le rapport à l'admin
            await context.bot.send_message(
                chat_id=self.config.ADMIN_ID,
                text=report,
                parse_mode="Markdown"
            )

            # Log pour le monitoring
            logger.info(f"Diffusion terminée: {stats['success']}/{total_users} succès en {total_time:.1f}s")

        except Exception as e:
            logger.error(f"Erreur critique dans broadcast_coupon_optimized: {e}")
            await context.bot.send_message(
                chat_id=self.config.ADMIN_ID,
                text=f"❌ **Erreur critique lors de la diffusion:**\n{str(e)}",
                parse_mode="Markdown"
            )

    async def show_daily_coupons(self, update, context):
        """Afficher chaque coupon du jour séparément (image/vidéo + texte)"""
        user_id = update.effective_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')

        today = date.today().isoformat()
        coupons = self.database.get_daily_coupons(today)
        coupons = list(reversed(coupons))

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

        # Envoyer chaque coupon un par un avec gestion d'erreur améliorée
        for coupon in coupons:
            try:
                caption = f"📌 {coupon['text']}\n🕒 {coupon['created_at']}"
                media_type = coupon.get('media_type', 'text')
                
                if media_type == "photo" and coupon.get('photo_path') and os.path.exists(coupon['photo_path']):
                    with open(coupon['photo_path'], 'rb') as img_file:
                        await context.bot.send_photo(
                            chat_id=user_id,
                            photo=img_file,
                            caption=caption
                        )
                elif media_type == "video" and coupon.get('video_path') and os.path.exists(coupon['video_path']):
                    # Paramètres pour l'envoi de vidéo
                    video_kwargs = {
                        'chat_id': user_id,
                        'caption': caption
                    }
                    
                    # Ajouter les métadonnées si disponibles
                    if coupon.get('video_duration'):
                        video_kwargs['duration'] = coupon['video_duration']
                    if coupon.get('video_width'):
                        video_kwargs['width'] = coupon['video_width']
                    if coupon.get('video_height'):
                        video_kwargs['height'] = coupon['video_height']
                    
                    # Envoyer la vidéo sans miniature
                    with open(coupon['video_path'], 'rb') as video_file:
                        video_kwargs['video'] = video_file
                        await context.bot.send_video(**video_kwargs)
                else:
                    await context.bot.send_message(
                        chat_id=user_id,
                        text=caption
                    )
                
                # Petite pause entre chaque coupon
                await asyncio.sleep(0.1)
                
            except Exception as e:
                logger.error(f"Erreur lors de l'envoi du coupon {coupon.get('coupon_id', 'unknown')} à {user_id}: {e}")

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

    async def get_broadcast_statistics(self, update, context):
        """Obtenir des statistiques sur les capacités de diffusion"""
        if str(update.effective_user.id) != str(self.config.ADMIN_ID):
            return

        user_count = self.database.get_user_count()
        estimated_time = (user_count // self.batch_size) * self.batch_delay
        stats_message = (
            f"📊 **STATISTIQUES DE DIFFUSION**\n\n"
            f"👥 **Utilisateurs totaux:** {user_count}\n"
            f"📦 **Taille des batches:** {self.batch_size}\n"
            f"⏱️ **Délai entre batches:** {self.batch_delay}s\n"
            f"🚀 **Vitesse estimée:** {self.batch_size/self.batch_delay:.1f} utilisateurs/seconde\n"
            f"⌛ **Temps estimé pour diffusion complète:** {estimated_time:.0f} secondes ({estimated_time/60:.1f} minutes)\n\n"
            f"📁 **Limites de fichiers:**\n"
            f"🖼️ Images: {self.MAX_PHOTO_SIZE/1024/1024:.0f} MB max\n"
            f"🎥 Vidéos: {self.MAX_VIDEO_SIZE/1024/1024:.0f} MB max"
        )

        await update.callback_query.message.reply_text(
            stats_message,
            parse_mode="Markdown"
        )
        await update.callback_query.answer()

    def cleanup_old_media(self, days_old=7):
        """Nettoyer les anciens fichiers média pour libérer l'espace disque"""
        try:
            import time
            from pathlib import Path
            
            current_time = time.time()
            deleted_count = 0
            freed_space = 0
            
            for file_path in Path(self.media_path).rglob("*"):
                if file_path.is_file():
                    # Calculer l'âge du fichier
                    file_age = (current_time - file_path.stat().st_mtime) / 86400  # en jours
                    
                    if file_age > days_old:
                        file_size = file_path.stat().st_size
                        try:
                            file_path.unlink()  # Supprimer le fichier
                            deleted_count += 1
                            freed_space += file_size
                            logger.info(f"Fichier supprimé: {file_path}")
                        except Exception as e:
                            logger.error(f"Erreur lors de la suppression de {file_path}: {e}")
            
            logger.info(f"Nettoyage terminé: {deleted_count} fichiers supprimés, {freed_space/1024/1024:.1f} MB libérés")
            return deleted_count, freed_space
            
        except Exception as e:
            logger.error(f"Erreur lors du nettoyage des médias: {e}")
            return 0, 0

    async def get_media_storage_info(self, update, context):
        """Afficher les informations sur l'espace de stockage des médias"""
        if str(update.effective_user.id) != str(self.config.ADMIN_ID):
            return

        try:
            import shutil
            from pathlib import Path
            
            # Calculer l'espace utilisé
            total_size = 0
            file_count = 0
            file_types = {'photo': 0, 'video': 0}
            
            for file_path in Path(self.media_path).rglob("*"):
                if file_path.is_file():
                    total_size += file_path.stat().st_size
                    file_count += 1
                    
                    # Catégoriser les fichiers
                    if 'photo' in file_path.name:
                        file_types['photo'] += 1
                    elif 'video' in file_path.name:
                        file_types['video'] += 1
            
            # Calculer l'espace libre
            free_space = shutil.disk_usage(self.media_path).free
            
            storage_info = (
                f"💾 **INFORMATIONS DE STOCKAGE**\n\n"
                f"📁 **Dossier:** {self.media_path}\n"
                f"📊 **Espace utilisé:** {total_size/1024/1024:.1f} MB\n"
                f"💿 **Espace libre:** {free_space/1024/1024/1024:.1f} GB\n"
                f"📄 **Nombre total de fichiers:** {file_count}\n\n"
                f"**Répartition par type:**\n"
                f"🖼️ Images: {file_types['photo']}\n"
                f"🎥 Vidéos: {file_types['video']}"
            )
            
            await update.callback_query.message.reply_text(
                storage_info,
                parse_mode="Markdown"
            )
            
        except Exception as e:
            await update.callback_query.message.reply_text(
                f"❌ Erreur lors de la récupération des informations de stockage: {str(e)}"
            )
        
        await update.callback_query.answer()