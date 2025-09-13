import random
import os
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts

class KamikazeGame(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Kamikaze"
        self.description = "Trouvez la station avec l'avion, les autres contiennent des kamikazes !"
        self.icon = "🛬"
        self.type = "1xbet"  # Type de jeu, peut être utilisé pour des statistiques ou des filtres
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu Kamikaze"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_kamikaze"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )]
        ])
        
        await query.edit_message_text(
            text=texts[language]["kamikaze_start"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche de Kamikaze"""
        query = update.callback_query
        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        
        # Générer un nombre aléatoire entre 1 et 5 pour choisir la station avec l'avion
        safe_station = random.randint(1, 5)
        
        # Obtenir l'image correspondante
        image_path = self.get_station_image(safe_station)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Message de résultat
        result_message = texts[language]["kamikaze_result"].format(position=safe_station)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_kamikaze"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_main"
            )]
        ])
        
        # Supprimer le message précédent pour éviter les conflits
        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")
        
        # Vérifier si l'image existe
        if os.path.exists(image_path):
            with open(image_path, 'rb') as photo:
                await context.bot.send_photo(
                    chat_id=user_id,
                    photo=photo,
                    caption=result_message,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
        else:
            # Si l'image n'existe pas, envoyer un nouveau message texte
            await context.bot.send_message(
                chat_id=user_id,
                text=result_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
    def get_station_image(self, station_number):
        """Obtenir le chemin de l'image de la station correspondante"""
        return f"media/games/kamikaze/kamikaze_{station_number}.jpg"
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }