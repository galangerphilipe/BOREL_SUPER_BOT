import logging
import sys
import os
from core.bot import TelegramBot
from utils.database import Database

# Configuration du logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Importer keep_alive seulement si nécessaire
try:
    from keep_alive import keep_alive
    keep_alive()
    logger.info("✅ Keep-alive activé")
except ImportError:
    logger.warning("⚠️ Keep-alive non disponible")


def main():
    """Point d'entrée principal du bot"""
    db = Database()

    try:
        logger.info("🎯 Initialisation du bot Telegram...")

        # Vérifier si une autre instance tourne déjà (via DB lock)
        if not db.acquire_lock():
            logger.error("❌ Une autre instance du bot est déjà en cours d'exécution!")
            sys.exit(1)

        # Vérifier qu'on n’a pas déjà marqué en mémoire
        if 'BOT_RUNNING' in os.environ:
            logger.error("❌ Une instance du bot est déjà en cours d'exécution (via env)!")
            sys.exit(1)

        # Marquer comme en cours d'exécution
        os.environ['BOT_RUNNING'] = 'true'

        # Créer et démarrer le bot
        bot = TelegramBot()
        bot.start()

    except KeyboardInterrupt:
        logger.info("🛑 Arrêt demandé par l'utilisateur")
        sys.exit(0)
    except Exception as e:
        logger.error(f"❌ Erreur fatale: {e}")
        sys.exit(1)
    finally:
        # Nettoyer le marqueur d'exécution
        os.environ.pop('BOT_RUNNING', None)

        # Libérer le verrou en DB
        db.release_lock()

        logger.info("🧹 Nettoyage terminé")


if __name__ == "__main__":
    main()
