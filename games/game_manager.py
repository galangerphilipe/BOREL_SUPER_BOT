from telegram import InlineKeyboardButton, InlineKeyboardMarkup
from games.crash.crash_game import CrashGame
from games.fortune_wheel.wheel_game import WheelGame
from games.game_of_thrones.game_of_thrones import GameOfThrones
from games.games_mines.games_mines import GamesMinesGame
from games.kamikaze.kamikaze import KamikazeGame
from games.swamp_lannd.swamp_land import SwampLandGame
from games.thimbles.thimbles import ThimblesGame
from games.under_over_7.under_over_7 import UnderOver7Game
from games.casino_mines.casino_mines import CasinoMinesGame
from utils.helpers import load_texts

class GameManager:
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.texts = load_texts()
        
        self.games = {
            'crash': CrashGame(config, database),
            'Apple Of Fortune': WheelGame(config, database),
            'Under Over 7' : UnderOver7Game(config, database),
            'game of thrones': GameOfThrones(config, database),  # Exemple de jeu supplémentaire
            'kamikaze': KamikazeGame(config, database),
            'thimbles': ThimblesGame(config, database),
            'swamp_land': SwampLandGame(config, database),
            'games_mines': GamesMinesGame(config, database),  # Assurez-vous que ce jeu est importé
            'casino_mines': CasinoMinesGame(config, database),  # Assurez-vous que ce jeu est importé
            # Ajouter d'autres jeux ici
        }
        
    def get_available_games(self):
        """Obtenir la liste des jeux disponibles"""
        return {key: game.get_game_info() for key, game in self.games.items()}
        
    async def show_games_list(self, update, context):
        """Afficher la liste des jeux"""
        if update.callback_query:
            query = update.callback_query
            user_id = query.from_user.id
            await query.answer()
        else:
            user_id = update.effective_user.id
            query = None
        
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        # Créer le clavier avec les jeux
        keyboard = []
        games = self.get_available_games()
        
        for game_key, game_info in games.items():
           if game_info.get('type') == "1xbet":
                keyboard.append([InlineKeyboardButton(
                    f"{game_info['icon']} {game_info['name']}",
                    callback_data=f"game_{game_key}"
                )])
            
        # Ajouter le bouton retour
        keyboard.append([InlineKeyboardButton(
            self.texts[language]["back_button"], 
            callback_data="main_menu"
        )])
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        text = self.texts[language]["select_game"]
        
        if query:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        
    async def select_game(self, update, context):
        """Sélectionner un jeu"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        game_key = query.data.replace('game_', '')
        
        if game_key not in self.games:
            return
            
        game = self.games[game_key]
        game_info = game.get_game_info()
        
        await self.show_game_options(query, context, game_key, game_info)
            
    async def show_game_options(self, query, context, game_key, game_info):
        """Afficher les options du jeu"""
        user_id = query.from_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        keyboard = InlineKeyboardMarkup([
            [InlineKeyboardButton(
                self.texts[language]["new_game"], 
                callback_data=f"start_game_{game_key}"
            )],
            [InlineKeyboardButton(
                self.texts[language]["back_button"], 
                callback_data="back_games"
            )],
            [InlineKeyboardButton(
                self.texts[language]["main_menu"], 
                callback_data="main_menu"
            )]
        ])
        
        await query.edit_message_text(
            text=self.texts[language]["game_selected"].format(
                game_name=game_info['name'],
                game_description=game_info['description']
            ),
            reply_markup=keyboard,
            parse_mode="HTML"
        )
        
    async def start_game(self, update, context):
        """Démarrer un jeu"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        game_key = query.data.replace('start_game_', '')
        
        if game_key in self.games:
            game = self.games[game_key]
            await game.start_game(update, context, user_id)

    async def handle_play_crash(self, update, context):
        """Gérer le bouton 'Play' pour le jeu Crash"""
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        if 'crash' in self.games:
            game = self.games['crash']
            await game.play_round(update, context, user_id)
    async def handle_play_apple_of_fortune(self, update, context):
        """Gérer le bouton 'Play' pour le jeu Apple Of Fortune"""
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        if 'Apple Of Fortune' in self.games:
            game = self.games['Apple Of Fortune']
            await game.play_round(update, context, user_id)
    

    async def handle_play_under_over_7(self, update, context):
        """Gérer le bouton 'Play' pour le jeu Under Over 7 """
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        if 'Under Over 7' in self.games:
            game = self.games['Under Over 7']
            await game.play_round(update, context, user_id)

    async def handle_play_game_of_thrones(self, update, context):
        """Gérer le bouton 'Play' pour le jeu Witch: Game of Thrones"""
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        if 'game of thrones' in self.games:
            game = self.games['game of thrones']
            await game.play_round(update, context, user_id)

    async def handle_play_kamikaze(self, update, context):
        """Gérer le bouton 'Play' pour le jeu kamikaze"""
        query = update.callback_query
        await query.answer()
        user_id = query.from_user.id
        if 'kamikaze' in self.games:
            game = self.games['kamikaze']
            await game.play_round(update, context, user_id)
    
    async def handle_play_thimbles(self, update, context):
        """Gérer le jeu Thimbles"""
        user_id = update.callback_query.from_user.id
        game = self.games.get('thimbles')
        if game:
            await game.play_round(update, context, user_id)
    
    async def handle_play_swamp_land(self, update, context):
        """Gérer le jeu Swamp Land"""
        user_id = update.callback_query.from_user.id
        game = self.games.get('swamp_land')
        if game:
            await game.play_round(update, context, user_id)

    async def handle_play_games_mines(self, update, context):
        """Gérer le jeu Games mines"""
        user_id = update.callback_query.from_user.id
        game = self.games.get('games_mines')
        if game:
            await game.play_round(update, context, user_id)

    async def handle_play_casino_mines(self, update, context):
        """Gérer le jeu Casino Mines"""
        user_id = update.callback_query.from_user.id
        game = self.games.get('casino_mines')
        if game:
            await game.play_round(update, context, user_id)
            
    def is_waiting_for_account_id(self, user_id):
        """Vérifier si l'utilisateur attend de saisir un ID de compte"""
        user_data = self.database.get_user(user_id)
        return user_data.get('waiting_for_account_id') is not None
        
    async def handle_account_id_input(self, update, context, account_id):
        """Gérer la saisie d'ID de compte"""
        user_id = update.effective_user.id
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        # Sauvegarder l'ID et supprimer l'état d'attente
        self.database.update_user(user_id, {
            'account_id': account_id,
            'waiting_for_account_id': None
        })
        
        await update.message.reply_text(
            self.texts[language]["account_id_saved"],
            parse_mode="HTML"
        )
        
        # Retourner au menu des jeux
        # Simuler un callback query pour réutiliser le code existant
        class MockQuery:
            def __init__(self, user_id):
                self.from_user = type('obj', (object,), {'id': user_id})
                
            async def answer(self):
                pass
                
            async def edit_message_text(self, **kwargs):
                await context.bot.send_message(
                    chat_id=user_id,
                    **kwargs
                )
                
        mock_query = MockQuery(user_id)
        update.callback_query = mock_query
        await self.show_games_list(update, context)
    
    async def show_1win_games_list(self, update, context):
        """Afficher la liste des jeux dont le type est '1win'"""
        if update.callback_query:
            query = update.callback_query
            user_id = query.from_user.id
            await query.answer()
        else:
            user_id = update.effective_user.id
            query = None

        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')

        # Créer le clavier avec les jeux de type '1win'
        keyboard = []
        games = self.get_available_games()
        for game_key, game_info in games.items():
            if game_info.get('type')  == "1win":
                keyboard.append([InlineKeyboardButton(
                    f"{game_info['icon']} {game_info['name']}",
                    callback_data=f"game_{game_key}"
                )])

        # Ajouter le bouton retour
        keyboard.append([InlineKeyboardButton(
            self.texts[language]["back_button"],
            callback_data="main_menu"
        )])

        reply_markup = InlineKeyboardMarkup(keyboard)
        text = self.texts[language].get("select_game", "Sélectionnez un jeu :")

        if query:
            await query.edit_message_text(
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )
        else:
            await context.bot.send_message(
                chat_id=user_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode="HTML"
            )