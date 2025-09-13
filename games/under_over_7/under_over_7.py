import random
import os
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts, update_game_time

class UnderOver7Game(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Under Over 7"
        self.description = "Devinez si la somme des dés sera inférieure, supérieure ou égale à 7 !"
        self.icon = "🎲"
        self.type = "1xbet"  # Type de jeu, peut être utilisé pour des statistiques ou des filtres
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu Under Over 7"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_under_over_7"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )]
        ])
        
        try:
            await query.edit_message_text(
                text=texts[language]["under_over_7_game_start"],
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Erreur lors de l'affichage du menu Under Over 7: {e}")
            # Essayer sans parse_mode en cas d'erreur HTML
            await query.edit_message_text(
                text="🎲 Under Over 7 - Jeu de dés disponible !",
                reply_markup=keyboard
            )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche d'Under Over 7"""
        query = update.callback_query

        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        
        # Simuler le lancement de deux dés
        rand = random.randint(1, 3)
        
        
        # Déterminer le résultat
        if rand == 1:
            result_type = "under"
            result_key = "under_7_result"
        elif rand == 2:
            result_type = "over"
            result_key = "over_7_result"
        else:  # total == 7
            result_type = "equal"
            result_key = "equal_7_result"
        
        # Obtenir l'image correspondante
        image_path = self.get_result_image(result_type)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Message de résultat avec les dés et le total
        result_message = texts[language][result_key]
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_under_over_7"
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
            # Si l'image n'existe pas, envoyer juste le texte
            await query.edit_message_text(
                text=result_message,
                reply_markup=keyboard,
                parse_mode="HTML"
            )
            
    def get_result_image(self, result_type):
        """Obtenir le chemin de l'image correspondante au résultat"""
        images = {
            "under": "media/games/under_over_7/under.jpg",
            "over": "media/games/under_over_7/over.jpg", 
            "equal": "media/games/under_over_7/7.jpg"
        }
        return images.get(result_type, "media/under_over_7/equal.jpg")
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }