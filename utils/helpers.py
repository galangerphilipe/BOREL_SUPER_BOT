import json
import os
import time

def load_texts():
    """Charger les textes multilingues"""
    try:
        with open('data/languages.json', 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        # Retourner des textes par défaut si le fichier n'existe pas
        return get_default_texts()
        
def get_default_texts():
    """Obtenir les textes par défaut"""
    return {
        "fr": {
            "choose_language": "🌍 Choisissez votre langue:",
            "start": """<b><i>🚀 Bienvenue dans le bot de jeux !</i></b>

📌 <b>Inscriptions recommandées :</b>
🎰 <a href="{links[1win]}">1win</a> - Code promo: <code>{promo_code}</code>
🏆 <a href="{links[1xbet]}">1XBet</a> - Code promo: <code>{promo_code}</code>

👇 Utilisez le menu ci-dessous pour naviguer""",
            "group_required": """📢 <b>Accès aux jeux</b>

Pour utiliser ce bot, vous devez rejoindre notre groupe Telegram :
👉 Rejoignez le groupe : {telegram_group}

Cliquez sur <b>Vérifier</b> après avoir rejoint le groupe""",
            "verify_button": "✅ Vérifier",
            "verified": "✅ Vérification réussie ! Vous pouvez maintenant accéder aux jeux.",
            "not_member": "❌ Vous n'avez pas encore rejoint notre groupe. Veuillez rejoindre le groupe et cliquer sur Vérifier.",
            "verification_error": "❌ Erreur lors de la vérification. Réessayez plus tard.",
            "how_to_play": "🎥 Comment jouer",
            "games_menu": "🎮 Jeux disponibles",
            "referral_menu": "👥 Parrainage",
            "change_language": "🌍 Changer de langue",
            "select_game": "🎮 <b>Sélectionnez un jeu</b>",
            "back_button": "⬅️ Retour",
            "main_menu": "🏠 Menu principal",
            "enter_account_id": "🆔 Veuillez entrer votre ID de compte 1xBet:",
            "account_id_saved": "✅ ID de compte sauvegardé avec succès !",
            "game_selected": "<b>🎮 {game_name}</b>\n\n{game_description}",
            "new_game": "🎲 Nouvelle partie",
            "crash_game_start": "✈️ <b>Jeu Crash</b>\n\nCliquez sur Jouer pour prédire le crash !",
            "play_button": "🎮 Jouer",
            "play_again": "🔄 Rejouer",
            "crash_result": "✈️ L'avion a crashé à <b>{value}</b> !",
            "referral_info": """👥 <b>Système de parrainage</b>

🏆 Vos parrainages: {referrals_count}
💰 Votre solde: {balance} points

🔗 <b>Votre lien de parrainage:</b>
{referral_link}

💡 <b>Comment ça marche:</b>
• Partagez votre lien avec vos amis
• Gagnez {bonus} points pour chaque {min_referrals} parrainages
• Plus vous parrainez, plus vous gagnez !""",
            "language_changed": "✅ Langue changée avec succès !",
            "wheel_game_start": "🎰 <b>Roue de la Fortune</b>\n\nTournez la roue et tentez votre chance !",
            "wheel_result": "🎰 La roue s'est arrêtée sur: <b>{result}</b>",
            "game_cooldown": "⏳ Veuillez attendre avant de rejouer. Réessayez dans quelques secondes."
        },
        "en": {
            "choose_language": "🌍 Choose your language:",
            "start": """<b><i>🚀 Welcome to the gaming bot!</i></b>

📌 <b>Recommended registrations:</b>
🎰 <a href="{links[1win]}">1win</a> - Promo code: <code>{promo_code}</code>
🏆 <a href="{links[1xbet]}">1XBet</a> - Promo code: <code>{promo_code}</code>

👇 Use the menu below to navigate""",
            "group_required": """📢 <b>Game Access</b>

To use this bot, you must join our Telegram group:
👉 Join the group : {telegram_group}

Click <b>Verify</b> after joining the group""",
            "verify_button": "✅ Verify",
            "verified": "✅ Verification successful! You can now access the games.",
            "not_member": "❌ You haven't joined our group yet. Please join the group and click Verify.",
            "verification_error": "❌ Verification error. Try again later.",
            "how_to_play": "🎥 How to play",
            "games_menu": "🎮 Available games",
            "referral_menu": "👥 Referral",
            "change_language": "🌍 Change language",
            "select_game": "🎮 <b>Select a game</b>",
            "back_button": "⬅️ Back",
            "main_menu": "🏠 Main menu",
            "enter_account_id": "🆔 Please enter your 1xBet account ID:",
            "account_id_saved": "✅ Account ID saved successfully!",
            "game_selected": "<b>🎮 {game_name}</b>\n\n{game_description}",
            "new_game": "🎲 New game",
            "crash_game_start": "✈️ <b>Crash Game</b>\n\nClick Play to predict the crash!",
            "play_button": "🎮 Play",
            "play_again": "🔄 Play again",
            "crash_result": "✈️ The plane crashed at <b>{value}</b>!",
            "referral_info": """👥 <b>Referral System</b>

🏆 Your referrals: {referrals_count}
💰 Your balance: {balance} points

🔗 <b>Your referral link:</b>
{referral_link}

💡 <b>How it works:</b>
• Share your link with friends
• Earn {bonus} points for every {min_referrals} referrals
• The more you refer, the more you earn!""",
            "language_changed": "✅ Language changed successfully!",
            "wheel_game_start": "🎰 <b>Wheel of Fortune</b>\n\nSpin the wheel and try your luck!",
            "wheel_result": "🎰 The wheel stopped on: <b>{result}</b>",
            "game_cooldown": "⏳ Please wait before playing again. Try again in a few seconds."
        }
    }

def check_cooldown(user_id, game_name, database, cooldown_duration=30):
    """Vérifier si l'utilisateur peut jouer (cooldown)"""
    user_data = database.get_user(user_id)
    last_game_times = user_data.get('last_game_time', {})
    
    if game_name in last_game_times:
        last_time = last_game_times[game_name]
        current_time = time.time()
        
        if current_time - last_time < cooldown_duration:
            return False
            
    return True

def update_game_time(user_id, game_name, database):
    """Mettre à jour le temps de dernière partie"""
    user_data = database.get_user(user_id)
    last_game_times = user_data.get('last_game_time', {})
    last_game_times[game_name] = time.time()
    
    database.update_user(user_id, {'last_game_time': last_game_times}) 