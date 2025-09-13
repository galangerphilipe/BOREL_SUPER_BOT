import json
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="data/users.json", coupons_path="data/coupons.json"):
        self.db_path = db_path
        self.coupons_path = coupons_path
        self.users = self._load_data(self.db_path)
        self.coupons = self._load_data(self.coupons_path)
        
    def _load_data(self, path):
        """Charger les données depuis le fichier JSON"""
        try:
            if os.path.exists(path):
                with open(path, 'r', encoding='utf-8') as f:
                    return json.load(f)
            return {}
        except Exception as e:
            print(f"Erreur lors du chargement de la base de données: {e}")
            return {}
            
    def _save_data(self, data, path):
        """Sauvegarder les données dans le fichier JSON"""
        try:
            os.makedirs(os.path.dirname(path), exist_ok=True)
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la base de données: {e}")
            
    def get_user(self, user_id):
        """Obtenir les données d'un utilisateur"""
        user_id = str(user_id)
        if user_id not in self.users:
            # Créer un nouvel utilisateur avec des valeurs par défaut
            self.users[user_id] = {
                'id': user_id,
                'language': 'fr',
                'verified': False,
                'account_id': None,
                'referrer': None,
                'referrals': [],
                'balance': 0,
                'games_played': {},
                'last_game_time': {},
                'created_at': datetime.now().isoformat(),
                'waiting_for_account_id': None,
                'waiting_for_question': False,
                'waiting_for_coupon': False
            }
            self._save_data(self.users, self.db_path)
            
        return self.users[user_id]
        
    def update_user(self, user_id, data):
        """Mettre à jour les données d'un utilisateur"""
        user_id = str(user_id)
        user_data = self.get_user(user_id)
        user_data.update(data)
        user_data['updated_at'] = datetime.now().isoformat()
        self.users[user_id] = user_data
        self._save_data(self.users, self.db_path)
        
    def add_coupon(self, coupon_data):
        """Ajouter un coupon à la base de données"""
        coupon_id = coupon_data['coupon_id']
        self.coupons[coupon_id] = coupon_data
        self._save_data(self.coupons, self.coupons_path)
        
    def get_daily_coupons(self, date_str):
        """Obtenir tous les coupons pour une date donnée"""
        return [coupon for coupon in self.coupons.values() if coupon['date'] == date_str]
        
    def get_all_users(self):
        """Obtenir tous les utilisateurs"""
        return self.users
        
    def get_user_count(self):
        """Obtenir le nombre d'utilisateurs"""
        return len(self.users)
        
    def get_verified_users(self):
        """Obtenir les utilisateurs vérifiés"""
        return {uid: user for uid, user in self.users.items() if user.get('verified', False)}