# SUPER_BOT BY UNITECHS

Bot Telegram multifonction pour la gestion de communauté, jeux, parrainage et navigation interactive.

## Fonctionnalités principales

- **Vérification d’adhésion au groupe** : Vérifie si l’utilisateur a rejoint un groupe Telegram spécifique avant d’accéder aux fonctionnalités.
- **Système de parrainage** : Génération et gestion de liens de parrainage pour inviter de nouveaux membres.
- **Navigation par menus** : Menus interactifs pour une expérience utilisateur fluide.
- **Jeux intégrés** : Plusieurs mini-jeux accessibles via le bot.
- **Gestion de base de données** : Stockage des utilisateurs, parrainages et scores.
- **Personnalisation multilingue** : Support du français et de l’anglais.

## Installation

1. **Cloner le dépôt**
   ```bash
   git clone https://github.com:jeffJeffrey/BOREL_SUPER_BOT.git
   cd SUPER_BOT
   ```

2. **Installer les dépendances**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurer le bot**
   - Renommez `config/settings_example.py` en `config/settings.py`
   - Renseignez votre token Telegram et les paramètres nécessaires.

4. **Lancer le bot**
   ```bash
   python main.py
   ```

## Structure du projet

```
SUPER_BOT/
├── core/           # Logique principale du bot (navigation, vérification, parrainage)
├── games/          # Modules de jeux
├── utils/          # Outils (image, base de données, helpers)
├── config/         # Fichiers de configuration
├── main.py         # Point d’entrée du bot
└── README.md
```

## Dépendances principales

- python-telegram-bot
- Pillow
- httpx

## Personnalisation

- Ajoutez vos propres jeux dans le dossier `games/`
- Modifiez les textes dans `utils/helpers.py` ou les fichiers de langues

## Licence

Ce projet est sous licence MIT. Voir le fichier [LICENSE](LICENSE) pour plus d’informations.

---

© 2025 UNITECHS. Tous droits réservés.