#!/bin/bash

# Script de démarrage pour l'application de messagerie Docker

set -e

echo "🚀 Démarrage de l'application de messagerie..."

# Fonction pour afficher l'aide
show_help() {
    echo "Usage: $0 [COMMAND]"
    echo ""
    echo "Commandes disponibles:"
    echo "  start     - Démarrer l'application"
    echo "  stop      - Arrêter l'application"
    echo "  restart   - Redémarrer l'application"
    echo "  logs      - Afficher les logs"
    echo "  status    - Afficher le statut des conteneurs"
    echo "  migrate   - Appliquer les migrations"
    echo "  shell     - Ouvrir un shell dans le conteneur web"
    echo "  build     - Reconstruire les images"
    echo "  clean     - Nettoyer les conteneurs et images non utilisés"
    echo "  help      - Afficher cette aide"
}

# Fonction pour démarrer l'application
start_app() {
    echo "📦 Construction et démarrage des conteneurs..."
    sudo docker-compose up --build -d
    echo "✅ Application démarrée !"
    echo "🌐 Accédez à l'application sur: http://localhost:8000"
    echo "🔧 Interface d'administration: http://localhost:8000/admin"
}

# Fonction pour arrêter l'application
stop_app() {
    echo "🛑 Arrêt des conteneurs..."
    sudo docker-compose down
    echo "✅ Application arrêtée !"
}

# Fonction pour redémarrer l'application
restart_app() {
    echo "🔄 Redémarrage de l'application..."
    stop_app
    start_app
}

# Fonction pour afficher les logs
show_logs() {
    echo "📋 Affichage des logs..."
    sudo docker-compose logs -f
}

# Fonction pour afficher le statut
show_status() {
    echo "📊 Statut des conteneurs:"
    sudo docker-compose ps
}

# Fonction pour appliquer les migrations
run_migrations() {
    echo "🗄️ Application des migrations..."
    sudo docker-compose exec web python manage.py migrate
    echo "✅ Migrations appliquées !"
}

# Fonction pour ouvrir un shell
open_shell() {
    echo "🐚 Ouverture d'un shell dans le conteneur web..."
    sudo docker-compose exec web bash
}

# Fonction pour reconstruire
rebuild() {
    echo "🔨 Reconstruction des images..."
    sudo docker-compose build --no-cache
    echo "✅ Images reconstruites !"
}

# Fonction pour nettoyer
cleanup() {
    echo "🧹 Nettoyage des ressources Docker..."
    sudo docker system prune -f
    echo "✅ Nettoyage terminé !"
}

# Gestion des arguments
case "${1:-start}" in
    start)
        start_app
        ;;
    stop)
        stop_app
        ;;
    restart)
        restart_app
        ;;
    logs)
        show_logs
        ;;
    status)
        show_status
        ;;
    migrate)
        run_migrations
        ;;
    shell)
        open_shell
        ;;
    build)
        rebuild
        ;;
    clean)
        cleanup
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "❌ Commande inconnue: $1"
        show_help
        exit 1
        ;;
esac 