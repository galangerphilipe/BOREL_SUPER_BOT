# Utiliser une image de base Python
FROM python:3.13-slim-bullseye

# Update system packages to reduce vulnerabilities

# Définir le répertoire de travail
WORKDIR /app

# Copier les fichiers de configuration
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier le reste des fichiers de l'application
COPY . .

# Exposer le port pour le serveur Flask
EXPOSE 8090

# Commande pour démarrer le bot
CMD ["python", "main.py"]