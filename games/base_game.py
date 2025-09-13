from abc import ABC, abstractmethod
from utils.image_processor import ImageProcessor

class BaseGame(ABC):
    def __init__(self, config, database):
        self.config = config
        self.database = database
        self.image_processor = ImageProcessor()
        
    @abstractmethod
    async def start_game(self, update, context, user_id):
        """Démarrer le jeu"""
        pass
        
    @abstractmethod
    async def play_round(self, update, context, user_id):
        """Jouer une manche"""
        pass
        
    @abstractmethod
    def get_game_info(self):
        """Obtenir les informations du jeu"""
        return {
            'name': self.name,
            'description': self.description,
            'icon': self.icon,
            'type': self.type
        }
        
    async def request_account_id(self, update, context, user_id):
        """Demander l'ID du compte"""
        user_data = self.database.get_user(user_id)
        language = user_data.get('language', 'fr')
        
        from utils.helpers import load_texts
        texts = load_texts()
        
        await context.bot.send_message(
            chat_id=user_id,
            text=texts[language]["enter_account_id"],
            parse_mode="HTML"
        )
        
        # Marquer l'utilisateur comme en attente d'ID
        self.database.update_user(user_id, {'waiting_for_account_id': self.name})
