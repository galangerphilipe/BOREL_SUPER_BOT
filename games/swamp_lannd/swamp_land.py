import random
import os
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts

class SwampLandGame(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Swamp Land"
        self.description = "Aidez la grenouille à choisir le bon nénuphar pour sauter !"
        self.icon = "🐸"
        self.type = "1xbet"  # Type de jeu, peut être utilisé pour des statistiques ou des filtres
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu Swamp Land"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_swamp_land"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )]
        ])
        
        try:
            await query.edit_message_text(
                text=texts[language]["swamp_land_game_start"],
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Erreur lors de l'affichage du menu Swamp Land: {e}")
            # Essayer sans parse_mode en cas d'erreur HTML
            await query.edit_message_text(
                text="🐸 Swamp Land - Jeu de la grenouille disponible !",
                reply_markup=keyboard
            )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche de Swamp Land"""
        query = update.callback_query

        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        
        # Générer un nombre aléatoire entre 1 et 5 pour choisir le nénuphar
        lily_pad_number = random.randint(1, 5)
        
        # Obtenir l'image correspondante
        image_path = self.get_swamp_land_image(lily_pad_number)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Message de résultat avec le numéro du nénuphar choisi
        result_message = texts[language]["swamp_land_result"].format(
            lily_pad=lily_pad_number
        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_swamp_land"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_main"
            )]
        ])

        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")
        
        # Vérifier si l'image existe
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=result_message,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'image: {e}")
                # Fallback: envoyer juste le texte
                await context.bot.send_message(
                    chat_id=user_id,
                    text=result_message,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
        else:
            # Si l'image n'existe pas, envoyer juste le texte
            try:
                await query.edit_message_text(
                    text=result_message,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except:
                await query.edit_message_text(
                    text=result_message,
                    reply_markup=keyboard
                )
            
    def get_swamp_land_image(self, lily_pad_number):
        """Obtenir le chemin de l'image correspondante au nénuphar"""
        return f"media/games/swamp_land/swamp_land_{lily_pad_number}.jpg"
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }