# 🐳 Application de Messagerie - Version Conteneurisée

Cette application de messagerie est entièrement conteneurisée avec Docker et Docker Compose, offrant une solution portable et cohérente pour le développement et le déploiement.

## 🚀 Démarrage rapide

### Prérequis
- Docker installé sur votre système
- Docker Compose installé
- Permissions sudo pour exécuter Docker

### Utilisation avec le script de démarrage (recommandé)

```bash
# Démarrer l'application
./start.sh start

# Arrêter l'application
./start.sh stop

# Redémarrer l'application
./start.sh restart

# Voir les logs
./start.sh logs

# Vérifier le statut
./start.sh status

# Appliquer les migrations
./start.sh migrate

# Ouvrir un shell dans le conteneur
./start.sh shell
```

### Utilisation manuelle avec Docker Compose

```bash
# Démarrer les services
sudo docker-compose up --build -d

# Voir les logs
sudo docker-compose logs -f

# Arrêter les services
sudo docker-compose down

# Appliquer les migrations
sudo docker-compose exec web python manage.py migrate

# Créer un superutilisateur
sudo docker-compose exec web python manage.py createsuperuser
```

## 🌐 Accès à l'application

- **Application principale** : http://localhost:8000
- **Interface d'administration Django** : http://localhost:8000/admin
- **API REST** : http://localhost:8000/api/

## 🏗️ Architecture

### Services Docker

1. **Service Web** (`web`)
   - Application Django
   - Port : 8000
   - Base image : Python 3.10-slim
   - Utilisateur non-root pour la sécurité

2. **Service Base de données** (`db`)
   - MySQL 5.7
   - Port : 3306 (interne)
   - Volume persistant : `mysql_data`

### Variables d'environnement

Le fichier `.env` contient les variables suivantes :
- `MYSQL_DATABASE` : Nom de la base de données
- `MYSQL_USER` : Utilisateur MySQL
- `MYSQL_PASSWORD` : Mot de passe utilisateur
- `MYSQL_ROOT_PASSWORD` : Mot de passe root MySQL

## 🔧 Configuration

### Dockerfile optimisé
- Image de base légère (Python 3.10-slim)
- Utilisateur non-root pour la sécurité
- Installation des dépendances système nécessaires
- Optimisation des couches Docker

### Docker Compose
- Health checks pour les deux services
- Dépendances entre services
- Volumes persistants pour les données
- Redémarrage automatique en cas d'échec

## 📁 Structure des fichiers

```
messaging_app/
├── Dockerfile              # Configuration de l'image Docker
├── docker-compose.yml      # Orchestration des services
├── .env                    # Variables d'environnement
├── .dockerignore          # Fichiers exclus du build
├── requirements.txt       # Dépendances Python
├── start.sh              # Script de démarrage
├── README_DOCKER.md      # Cette documentation
├── messaging_app/        # Application Django
│   ├── settings.py       # Configuration Django
│   └── ...
└── chats/               # Application de messagerie
    └── ...
```

## 🛠️ Commandes utiles

### Gestion des conteneurs
```bash
# Voir les conteneurs en cours d'exécution
sudo docker ps

# Voir tous les conteneurs
sudo docker ps -a

# Voir les images
sudo docker images

# Nettoyer les ressources non utilisées
sudo docker system prune -f
```

### Gestion de la base de données
```bash
# Se connecter à MySQL
sudo docker-compose exec db mysql -u root -p

# Sauvegarder la base de données
sudo docker-compose exec db mysqldump -u root -p messaging_db > backup.sql

# Restaurer la base de données
sudo docker-compose exec -T db mysql -u root -p messaging_db < backup.sql
```

### Développement
```bash
# Ouvrir un shell dans le conteneur web
sudo docker-compose exec web bash

# Exécuter des tests
sudo docker-compose exec web python manage.py test

# Collecter les fichiers statiques
sudo docker-compose exec web python manage.py collectstatic
```

## 🔒 Sécurité

- Utilisateur non-root dans le conteneur
- Variables d'environnement pour les secrets
- Fichier `.env` exclu du versioning
- Health checks pour la surveillance

## 🚨 Dépannage

### Problèmes courants

1. **Port déjà utilisé**
   ```bash
   # Vérifier les ports utilisés
   sudo netstat -tulpn | grep :8000
   ```

2. **Problèmes de permissions**
   ```bash
   # Ajouter l'utilisateur au groupe docker
   sudo usermod -aG docker $USER
   ```

3. **Base de données non accessible**
   ```bash
   # Vérifier les logs de la base de données
   sudo docker-compose logs db
   ```

4. **Migrations en échec**
   ```bash
   # Réinitialiser la base de données
   sudo docker-compose down -v
   sudo docker-compose up --build -d
   sudo docker-compose exec web python manage.py migrate
   ```

## 📈 Monitoring

### Health Checks
- **Web** : Vérification HTTP sur le port 8000
- **Database** : Ping MySQL avec mysqladmin

### Logs
```bash
# Logs en temps réel
sudo docker-compose logs -f

# Logs d'un service spécifique
sudo docker-compose logs -f web
sudo docker-compose logs -f db
```

## 🎯 Bonnes pratiques

1. **Toujours utiliser le script `start.sh`** pour la gestion
2. **Sauvegarder régulièrement** la base de données
3. **Nettoyer périodiquement** les ressources Docker
4. **Vérifier les logs** en cas de problème
5. **Utiliser les health checks** pour la surveillance

## 📞 Support

En cas de problème, vérifiez :
1. Les logs des conteneurs
2. Le statut des services
3. La configuration des variables d'environnement
4. Les permissions Docker

---

**Développé avec ❤️ et Docker** 