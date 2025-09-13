import random
import os
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts

class GamesMinesGame(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Games Mines"
        self.description = "Découvrez les trésors cachés sous les pavés !"
        self.icon = "💎"
        self.type = "1xbet"  # Type de jeu, peut être utilisé pour des statistiques ou des filtres
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu Games Mines"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_games_mines"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )]
        ])
        
        try:
            await query.edit_message_text(
                text=texts[language]["games_mines_start"],
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Erreur lors de l'affichage du menu Games Mines: {e}")
            # Essayer sans parse_mode en cas d'erreur HTML
            await query.edit_message_text(
                text="💎 Games Mines - Jeu des trésors cachés disponible !",
                reply_markup=keyboard
            )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche de Games Mines"""
        query = update.callback_query

        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        
        # Générer un nombre aléatoire entre 1 et 10 pour choisir la combinaison
        combination_number = random.randint(1, 10)
        
        # Obtenir l'image correspondante
        image_path = self.get_games_mines_image(combination_number)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Message de résultat avec la combinaison choisie
        result_message = texts[language]["games_mines_result"]
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_games_mines"
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
            
    def get_games_mines_image(self, combination_number):
        """Obtenir le chemin de l'image correspondante à la combinaison"""
        return f"media/games/games_mines/games_mines_{combination_number}.jpg"
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }