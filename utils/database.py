import sqlite3
import json
import os
from datetime import datetime

class Database:
    def __init__(self, db_path="data/database.db"):
        self.db_path = db_path
        self._init_database()
    
    def _init_database(self):
        """Initialiser la base de données SQLite"""
        # Créer le dossier data s'il n'existe pas
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Table des utilisateurs
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id TEXT PRIMARY KEY,
                language TEXT DEFAULT 'fr',
                verified BOOLEAN DEFAULT FALSE,
                account_id TEXT,
                referrer TEXT,
                referrals TEXT,  -- JSON string pour stocker la liste
                balance INTEGER DEFAULT 0,
                games_played TEXT,  -- JSON string pour stocker l'objet
                last_game_time TEXT,  -- JSON string pour stocker l'objet
                created_at TEXT,
                updated_at TEXT,
                waiting_for_account_id TEXT,
                waiting_for_question BOOLEAN DEFAULT FALSE,
                waiting_for_coupon BOOLEAN DEFAULT FALSE,
                FOREIGN KEY (referrer) REFERENCES users (id)
            )
        ''')
        
        # Table des coupons mise à jour
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS coupons (
                coupon_id TEXT PRIMARY KEY,
                date TEXT,
                text TEXT,
                media_type TEXT DEFAULT 'text',
                photo_path TEXT,
                video_path TEXT,
                created_at TEXT,
                admin_id TEXT,
                active BOOLEAN DEFAULT TRUE,
                -- Anciens champs optionnels pour compatibilité
                title TEXT,
                description TEXT,
                discount REAL,
                code TEXT,
                expires_at TEXT,
                max_uses INTEGER,
                current_uses INTEGER DEFAULT 0
            )
        ''')
        
        # Vérifier si la table existe déjà et ajouter les nouvelles colonnes si nécessaire
        cursor.execute("PRAGMA table_info(coupons)")
        columns = [column[1] for column in cursor.fetchall()]
        
        # Ajouter les nouvelles colonnes si elles n'existent pas
        new_columns = [
            ('text', 'TEXT'),
            ('media_type', 'TEXT DEFAULT \'text\''),
            ('photo_path', 'TEXT'),
            ('video_path', 'TEXT'),
            ('admin_id', 'TEXT')
        ]
        
        for column_name, column_type in new_columns:
            if column_name not in columns:
                try:
                    cursor.execute(f'ALTER TABLE coupons ADD COLUMN {column_name} {column_type}')
                    print(f"Colonne '{column_name}' ajoutée à la table coupons")
                except sqlite3.OperationalError as e:
                    print(f"Erreur lors de l'ajout de la colonne '{column_name}': {e}")
        
        conn.commit()
        conn.close()
    
    def _get_connection(self):
        """Obtenir une connexion à la base de données"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # Pour obtenir des résultats sous forme de dict
        return conn
    
    def get_user(self, user_id):
        """Obtenir les données d'un utilisateur"""
        user_id = str(user_id)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
        user_row = cursor.fetchone()
        
        if user_row:
            # Convertir la row en dictionnaire et désérialiser les champs JSON
            user_data = dict(user_row)
            user_data['referrals'] = json.loads(user_data['referrals']) if user_data['referrals'] else []
            user_data['games_played'] = json.loads(user_data['games_played']) if user_data['games_played'] else {}
            user_data['last_game_time'] = json.loads(user_data['last_game_time']) if user_data['last_game_time'] else {}
            user_data['verified'] = bool(user_data['verified'])
            user_data['waiting_for_question'] = bool(user_data['waiting_for_question'])
            user_data['waiting_for_coupon'] = bool(user_data['waiting_for_coupon'])
            conn.close()
            return user_data
        else:
            # Créer un nouvel utilisateur avec des valeurs par défaut
            new_user = {
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
                'updated_at': datetime.now().isoformat(),
                'waiting_for_account_id': None,
                'waiting_for_question': False,
                'waiting_for_coupon': False
            }
            
            cursor.execute('''
                INSERT INTO users (
                    id, language, verified, account_id, referrer, referrals,
                    balance, games_played, last_game_time, created_at, updated_at,
                    waiting_for_account_id, waiting_for_question, waiting_for_coupon
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                new_user['id'],
                new_user['language'],
                new_user['verified'],
                new_user['account_id'],
                new_user['referrer'],
                json.dumps(new_user['referrals']),
                new_user['balance'],
                json.dumps(new_user['games_played']),
                json.dumps(new_user['last_game_time']),
                new_user['created_at'],
                new_user['updated_at'],
                new_user['waiting_for_account_id'],
                new_user['waiting_for_question'],
                new_user['waiting_for_coupon']
            ))
            
            conn.commit()
            conn.close()
            return new_user
    
    def update_user(self, user_id, data):
        """Mettre à jour les données d'un utilisateur"""
        user_id = str(user_id)
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Obtenir l'utilisateur actuel
        current_user = self.get_user(user_id)
        
        # Mettre à jour les données
        current_user.update(data)
        current_user['updated_at'] = datetime.now().isoformat()
        
        # Préparer les données pour la mise à jour
        cursor.execute('''
            UPDATE users SET
                language = ?,
                verified = ?,
                account_id = ?,
                referrer = ?,
                referrals = ?,
                balance = ?,
                games_played = ?,
                last_game_time = ?,
                updated_at = ?,
                waiting_for_account_id = ?,
                waiting_for_question = ?,
                waiting_for_coupon = ?
            WHERE id = ?
        ''', (
            current_user['language'],
            current_user['verified'],
            current_user['account_id'],
            current_user['referrer'],
            json.dumps(current_user['referrals']),
            current_user['balance'],
            json.dumps(current_user['games_played']),
            json.dumps(current_user['last_game_time']),
            current_user['updated_at'],
            current_user['waiting_for_account_id'],
            current_user['waiting_for_question'],
            current_user['waiting_for_coupon'],
            user_id
        ))
        
        conn.commit()
        conn.close()
    
    def add_coupon(self, coupon_data):
        """Ajouter un coupon à la base de données"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Ajouter created_at si pas présent
        if 'created_at' not in coupon_data:
            coupon_data['created_at'] = datetime.now().isoformat()
        
        cursor.execute('''
            INSERT OR REPLACE INTO coupons (
                coupon_id, date, text, media_type, photo_path, video_path,
                created_at, admin_id, active, title, description, discount, 
                code, expires_at, max_uses, current_uses
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            coupon_data['coupon_id'],
            coupon_data.get('date'),
            coupon_data.get('text', ''),
            coupon_data.get('media_type', 'text'),
            coupon_data.get('photo_path'),
            coupon_data.get('video_path'),
            coupon_data['created_at'],
            coupon_data.get('admin_id'),
            coupon_data.get('active', True),
            # Anciens champs pour compatibilité
            coupon_data.get('title'),
            coupon_data.get('description'),
            coupon_data.get('discount', 0),
            coupon_data.get('code'),
            coupon_data.get('expires_at'),
            coupon_data.get('max_uses', 0),
            coupon_data.get('current_uses', 0)
        ))
        
        conn.commit()
        conn.close()
    
    def get_daily_coupons(self, date_str):
        """Obtenir tous les coupons pour une date donnée"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM coupons WHERE date = ? AND active = TRUE ORDER BY created_at DESC", (date_str,))
        coupons = cursor.fetchall()
        
        conn.close()
        return [dict(coupon) for coupon in coupons]
    
    def get_coupon(self, coupon_id):
        """Obtenir un coupon spécifique"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM coupons WHERE coupon_id = ?", (coupon_id,))
        coupon = cursor.fetchone()
        
        conn.close()
        return dict(coupon) if coupon else None
    
    def update_coupon_usage(self, coupon_id):
        """Incrémenter l'utilisation d'un coupon"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE coupons 
            SET current_uses = current_uses + 1 
            WHERE coupon_id = ?
        ''', (coupon_id,))
        
        conn.commit()
        conn.close()
    
    def get_all_users(self):
        """Obtenir tous les utilisateurs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users")
        users_rows = cursor.fetchall()
        
        users = {}
        for user_row in users_rows:
            user_data = dict(user_row)
            user_data['referrals'] = json.loads(user_data['referrals']) if user_data['referrals'] else []
            user_data['games_played'] = json.loads(user_data['games_played']) if user_data['games_played'] else {}
            user_data['last_game_time'] = json.loads(user_data['last_game_time']) if user_data['last_game_time'] else {}
            user_data['verified'] = bool(user_data['verified'])
            user_data['waiting_for_question'] = bool(user_data['waiting_for_question'])
            user_data['waiting_for_coupon'] = bool(user_data['waiting_for_coupon'])
            users[user_data['id']] = user_data
        
        conn.close()
        return users
    
    def get_user_count(self):
        """Obtenir le nombre d'utilisateurs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM users")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_verified_users(self):
        """Obtenir les utilisateurs vérifiés"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE verified = TRUE")
        users_rows = cursor.fetchall()
        
        users = {}
        for user_row in users_rows:
            user_data = dict(user_row)
            user_data['referrals'] = json.loads(user_data['referrals']) if user_data['referrals'] else []
            user_data['games_played'] = json.loads(user_data['games_played']) if user_data['games_played'] else {}
            user_data['last_game_time'] = json.loads(user_data['last_game_time']) if user_data['last_game_time'] else {}
            user_data['verified'] = bool(user_data['verified'])
            user_data['waiting_for_question'] = bool(user_data['waiting_for_question'])
            user_data['waiting_for_coupon'] = bool(user_data['waiting_for_coupon'])
            users[user_data['id']] = user_data
        
        conn.close()
        return users
    
    def delete_user(self, user_id):
        """Supprimer un utilisateur"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM users WHERE id = ?", (str(user_id),))
        
        conn.commit()
        conn.close()
    
    def get_users_by_referrer(self, referrer_id):
        """Obtenir tous les utilisateurs parrainés par un utilisateur"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM users WHERE referrer = ?", (str(referrer_id),))
        users_rows = cursor.fetchall()
        
        users = []
        for user_row in users_rows:
            user_data = dict(user_row)
            user_data['referrals'] = json.loads(user_data['referrals']) if user_data['referrals'] else []
            user_data['games_played'] = json.loads(user_data['games_played']) if user_data['games_played'] else {}
            user_data['last_game_time'] = json.loads(user_data['last_game_time']) if user_data['last_game_time'] else {}
            user_data['verified'] = bool(user_data['verified'])
            user_data['waiting_for_question'] = bool(user_data['waiting_for_question'])
            user_data['waiting_for_coupon'] = bool(user_data['waiting_for_coupon'])
            users.append(user_data)
        
        conn.close()
        return users
    
    def get_active_coupons(self):
        """Obtenir tous les coupons actifs"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM coupons WHERE active = TRUE ORDER BY created_at DESC")
        coupons = cursor.fetchall()
        
        conn.close()
        return [dict(coupon) for coupon in coupons]
    
    def deactivate_coupon(self, coupon_id):
        """Désactiver un coupon"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("UPDATE coupons SET active = FALSE WHERE coupon_id = ?", (coupon_id,))
        
        conn.commit()
        conn.close()
    
    def get_coupons_by_admin(self, admin_id):
        """Obtenir tous les coupons créés par un admin spécifique"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT * FROM coupons WHERE admin_id = ? ORDER BY created_at DESC", (str(admin_id),))
        coupons = cursor.fetchall()
        
        conn.close()
        return [dict(coupon) for coupon in coupons]
    
    def delete_coupon(self, coupon_id):
        """Supprimer définitivement un coupon"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        cursor.execute("DELETE FROM coupons WHERE coupon_id = ?", (coupon_id,))
        
        conn.commit()
        conn.close()
    
    def get_coupon_statistics(self):
        """Obtenir des statistiques sur les coupons"""
        conn = self._get_connection()
        cursor = conn.cursor()
        
        # Statistiques générales
        cursor.execute("SELECT COUNT(*) as total FROM coupons")
        total_coupons = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as active FROM coupons WHERE active = TRUE")
        active_coupons = cursor.fetchone()[0]
        
        cursor.execute("SELECT COUNT(*) as today FROM coupons WHERE date = ?", (datetime.now().date().isoformat(),))
        today_coupons = cursor.fetchone()[0]
        
        # Statistiques par type de média
        cursor.execute("SELECT media_type, COUNT(*) as count FROM coupons GROUP BY media_type")
        media_stats = cursor.fetchall()
        
        conn.close()
        
        return {
            'total_coupons': total_coupons,
            'active_coupons': active_coupons,
            'today_coupons': today_coupons,
            'media_stats': [dict(stat) for stat in media_stats]
        }
    
    def close(self):
        """Fermer la connexion (optionnel avec SQLite car auto-fermée)"""
        pass