import random
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts

class CrashGame(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Crash"
        self.description = "Prédiction de crash d'avion"
        self.icon = "✈️"
        self.type = "1xbet"
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu crash"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_crash"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )]
        ])
        
        await query.edit_message_text(
            text=texts[language]["crash_game_start"],
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche de crash"""
        query = update.callback_query

        # Supprimer le message précédent pour éviter les conflits
        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        crash_value = self.generate_crash_value()
        
        # Générer l'image avec la valeur
        image_path = await self.create_crash_image(crash_value)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_crash"
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
        
        with open(image_path, 'rb') as photo:
            await context.bot.send_photo(
                chat_id=user_id,
                photo=photo,
                caption=texts[language]["crash_result"].format(value=crash_value),
                reply_markup=keyboard,
                parse_mode="HTML"
            )
        #  delete the image after sending
        import os
        os.remove(image_path)
            
    def generate_crash_value(self):
        """Générer une valeur de crash aléatoire"""
        rand_val = random.random()
        
        if rand_val < 0.40:  # 40% < 2
            crash_point = random.uniform(1.0, 2.0)
        elif rand_val < 0.60:  # 20% 2-10
            crash_point = random.uniform(2.0, 10.0)
        elif rand_val < 0.80:  # 20% 10-25
            crash_point = random.uniform(10.0, 25.0)
        elif rand_val < 0.92:  # 12% 25-50
            crash_point = random.uniform(25.0, 50.0)
        else:  # 8% >50
            crash_point = random.uniform(50.0, 100.0)
            
        return round(crash_point, 2)
        
    async def create_crash_image(self, crash_value):
        """Créer une image avec la valeur de crash"""
        base_image = "media/games/crash/crash_base.png"
        output_path = f"media/games/crash/crash_result_{crash_value}.png"
        
        # Position où placer le texte (x, y)
        text_position = (680, 310)
        
        self.image_processor.add_text_to_image(
            base_image,
            str("x"+ str(crash_value)),
            text_position,
            output_path,
            font_size=65,
            color="white"
        )
        
        return output_path
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }