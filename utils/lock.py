import time
import logging

class BotLock:
    """
    Simple verrou basé sur la base de données (ou autre storage partagé).
    Ici on simule avec une table 'bot_lock' dans ta DB.
    """

    def __init__(self, database, lock_name="telegram_bot_lock"):
        self.db = database
        self.lock_name = lock_name
        self.acquired = False

    def acquire(self, timeout=5):
        """
        Essaye de poser un verrou en DB.
        Retourne True si succès, False sinon.
        """
        start = time.time()
        while time.time() - start < timeout:
            try:
                conn = self.db.get_connection()
                cur = conn.cursor()

                # Tenter d’insérer un verrou unique
                cur.execute("""
                    INSERT INTO bot_lock (name, created_at)
                    VALUES (%s, NOW())
                    ON CONFLICT (name) DO NOTHING
                """, (self.lock_name,))
                conn.commit()

                # Vérifier si c'est bien nous qui avons le lock
                cur.execute("SELECT name FROM bot_lock WHERE name=%s", (self.lock_name,))
                row = cur.fetchone()
                cur.close()
                conn.close()

                if row:
                    self.acquired = True
                    return True
            except Exception as e:
                logging.error(f"Erreur acquisition du lock: {e}")
            time.sleep(1)
        return False

    def release(self):
        """Libère le verrou"""
        if not self.acquired:
            return
        try:
            conn = self.db.get_connection()
            cur = conn.cursor()
            cur.execute("DELETE FROM bot_lock WHERE name=%s", (self.lock_name,))
            conn.commit()
            cur.close()
            conn.close()
            logging.info("🔓 Verrou libéré")
        except Exception as e:
            logging.error(f"Erreur libération du lock: {e}")
