import random
import os
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts, check_cooldown, update_game_time

class WheelGame(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Apple Of Fortune"
        self.description = "Choisir la bonne pomme pour gagner des récompenses !"
        self.icon = "🍎"
        self.type = "1xbet"  # Type de jeu, peut être utilisé pour des statistiques ou des filtres
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu de la pomme"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_wheel"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )]
        ])
        
        await query.edit_message_text(
            text=texts[language]["apple_game_start"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche de pommes"""
        query = update.callback_query
        
        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        winning_apple = random.randint(1, 5)
        
        # Obtenir l'image correspondante
        image_path = self.get_apple_image(winning_apple)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Message de résultat
        result_message = texts[language]["apple_result"].format(position=winning_apple)
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_wheel"
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
            
    def get_apple_image(self, apple_number):
        """Obtenir le chemin de l'image de la pomme correspondante"""
        return f"media/games/apple/apple_{apple_number}.jpeg"
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }