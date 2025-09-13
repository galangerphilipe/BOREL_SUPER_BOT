import random
import os
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts
class ThimblesGame(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Thimbles"
        self.description = "Trouvez où se cachent les 2 boules sous les 3 pots !"
        self.icon = "🥃"
        self.type = "1xbet"  # Type de jeu, peut être utilisé pour des statistiques ou des filtres
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu Thimbles"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_thimbles"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )]
        ])
        
        try:
            await query.edit_message_text(
                text=texts[language]["thimbles_game_start"],
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        except Exception as e:
            print(f"Erreur lors de l'affichage du menu Thimbles: {e}")
            # Essayer sans parse_mode en cas d'erreur HTML
            await query.edit_message_text(
                text="🥃 Thimbles - Jeu des gobelets disponible !",
                reply_markup=keyboard
            )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche de Thimbles"""
        query = update.callback_query
        
    
        
        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        ball_position = random.randint(1, 3)
        
        # Obtenir l'image correspondante
        image_path = self.get_thimbles_image(ball_position)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Message de résultat selon la position
        if ball_position == 1:
            result_message = texts[language]["thimbles_result_1"]
        elif ball_position == 2:
            result_message = texts[language]["thimbles_result_2"] 
        else:  # ball_position == 3
            result_message = texts[language]["thimbles_result_3"]
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_thimbles"
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
            
    def get_thimbles_image(self, position):
        """Obtenir le chemin de l'image correspondante à la position"""
        images = {
            1: "media/games/thimbles/thimbles_1.jpg",  
            2: "media/games/thimbles/thimbles_2.jpg",  
            3: "media/games/thimbles/thimbles_3.jpg" 
        }
        return images.get(position, "media/thimbles/thimbles_1.jpg")
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }