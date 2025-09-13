import random
import os
from games.base_game import BaseGame
from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from utils.helpers import load_texts

class CasinoMinesGame(BaseGame):
    def __init__(self, config, database):
        super().__init__(config, database)
        self.name = "Casino Mines"
        self.description = "Découvrez les trésors cachés dans les mines du casino !"
        self.type ="1win"
        self.icon = "💣"
        self.config = config
        
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu Casino Mines"""
        query = update.callback_query
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Récupérer les données de configuration
        promo_code = self.config.PROMO_CODE
        links = self.config.LINKS
        onewin_link = links.get('1win', 'http://1wyfui.life/?p=t974')
        xbet_link = links.get('1xbet', 'https://urls.fr/j0C9yU')
        
        # Construire le message avec les données de configuration
        start_message = texts[language]["casino_mines_start"].format(
            promo_code=promo_code,
            onewin_link=onewin_link,
            xbet_link=xbet_link

        )
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_button"], 
                callback_data="play_casino_mines"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="back_games"
            )],
            [InlineKeyboardButton(
                texts[language]["main_menu"], 
                callback_data="back_main"
            )]
        ])
        
        # Chemin de l'image
        image_path = "media/games/casino_mine/casino_mine_1.jpg"
        
        # Vérifier si l'image existe et l'envoyer
        if os.path.exists(image_path):
            try:
                with open(image_path, 'rb') as photo:
                    await context.bot.send_photo(
                        chat_id=user_id,
                        photo=photo,
                        caption=start_message,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
            except Exception as e:
                print(f"Erreur lors de l'envoi de l'image: {e}")
                # Fallback: envoyer juste le texte
                try:
                    await query.edit_message_text(
                        text=start_message,
                        reply_markup=keyboard,
                        parse_mode="HTML"
                    )
                except Exception as e2:
                    print(f"Erreur lors de l'affichage du menu Casino Mines: {e2}")
                    # Essayer sans parse_mode en cas d'erreur HTML
                    await query.edit_message_text(
                        text="💣 Casino Mines - Jeu des mines disponible !",
                        reply_markup=keyboard
                    )
        else:
            # Si l'image n'existe pas, envoyer juste le texte
            try:
                await query.edit_message_text(
                    text=start_message,
                    reply_markup=keyboard,
                    parse_mode="HTML"
                )
            except Exception as e:
                print(f"Erreur lors de l'affichage du menu Casino Mines: {e}")
                # Essayer sans parse_mode en cas d'erreur HTML
                await query.edit_message_text(
                    text="💣 Casino Mines - Jeu des mines disponible !",
                    reply_markup=keyboard
                )
        
    async def play_round(self, update, context, user_id):
        """Jouer une manche de Casino Mines"""
        query = update.callback_query

        try:
            await query.delete_message()
        except Exception as e:
            print(f"Erreur lors de la suppression du message: {e}")

        
        # Générer un nombre aléatoire entre 1 et 9 pour choisir la combinaison
        combination_number = random.randint(1, 95)
        
        # Obtenir l'image correspondante pour le résultat
        image_path = self.get_casino_mines_image(combination_number)
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        texts = load_texts()
        
        # Message de résultat avec la combinaison choisie
        result_message = texts[language]["casino_mines_result"]
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                texts[language]["play_again"], 
                callback_data="play_casino_mines"
            )],
            [InlineKeyboardButton(
                texts[language]["back_button"], 
                callback_data="start_casino_mines"
            )],
            [InlineKeyboardButton(
                texts[language]["main_menu"], 
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
            
    def get_casino_mines_image(self, combination_number):
        """Obtenir le chemin de l'image correspondante à la combinaison"""
        return f"media/games/casino_mine/casino_mine_{combination_number}.jpg"
        
    def get_game_info(self):
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }