import random
import os
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts

class GameOfThrones(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Witch: Game of Thrones"
        self.description = "Trouvez la potion non empoisonnée parmi les cinq pour survivre !"
        self.icon = "🧪",
        self.type = "1xbet"
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu Witch: Game of Thrones"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_game_of_thrones"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )]
        ])
        
        await query.edit_message_text(
            text=texts[language]["game_of_thrones_start"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche de Witch: Game of Thrones"""
        query = update.callback_query

        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        
        # Générer un nombre aléatoire entre 1 et 5 pour choisir la potion non empoisonnée
        safe_potion = random.randint(1, 5)
        
        # Obtenir l'image correspondante
        image_path = self.get_potion_image(safe_potion)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Message de résultat
        result_message = texts[language]["game_of_thrones_result"].format(position=safe_potion)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_game_of_thrones"
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
            
    def get_potion_image(self, potion_number):
        """Obtenir le chemin de l'image de la potion correspondante"""
        return f"media/games/game_of_thrones/potion_{potion_number}.jpg"
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }